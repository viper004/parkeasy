from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import redirect, render
import qrcode
from io import BytesIO
from django.core.files import File

from .decorators import account_login_required, admin_login_required, login_required
from .models import *

def home(request):
    return render(request,'index.html')


def login_user(request):
    if request.method == "POST":
        phone = request.POST.get('phone')
        dob = request.POST.get('dob')

        # Check Admin
        admin = Admin.objects.filter(phone=phone, dob=dob).first()
        if admin:
            request.session['admin_id'] = admin.id
            return redirect('admin_dashboard')

        # Check Resident User
        user = User.objects.filter(phone=phone, dob=dob).first()
        if user:
            request.session['user_id'] = user.id
            return redirect('user_dashboard')
            
        # ADD THIS: Check Security Staff
        # Note: SecurityStaff uses 'date_of_birth' field name in your model
        security = SecurityStaff.objects.filter(phone=phone, date_of_birth=dob).first()
        if security:
            request.session['security_id'] = security.id
            return redirect('security_dashboard')

        messages.error(request, 'Invalid credentials')
        return redirect('home')
    return redirect('home')

def security_dashboard(request):
    security_id = request.session.get('security_id')
    if not security_id:
        return redirect('home')
    
    security = SecurityStaff.objects.get(id=security_id)
    recent_logs = VehicleLog.objects.all()[:10]
    return render(request, 'security/security_dashboard.html', {
        'security': security,
        'recent_logs': recent_logs
        })

def gate_control(request):
    security_id = request.session.get('security_id')
    if not security_id or request.method != "POST":
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

    vehicle_number = request.POST.get('vehicle_number', '').strip().upper()
    vehicle = Vehicle.objects.filter(number=vehicle_number, is_approved=True).first()

    if not vehicle:
        return JsonResponse({'status': 'error', 'message': 'Vehicle not found or not approved'})

    # Toggle the status: If True, set to False. If False, set to True.
    vehicle.is_in = not vehicle.is_in 
    vehicle.save() # THIS IS THE CRITICAL STEP

    # Create a log entry for the history
    staff = SecurityStaff.objects.get(id=security_id)
    action = 'IN' if vehicle.is_in else 'OUT'
    VehicleLog.objects.create(vehicle=vehicle, staff=staff, action=action)

    return JsonResponse({
        'status': 'success',
        'vehicle_number': vehicle.number,
        'is_in': vehicle.is_in,
        'message': f'Vehicle marked as {action}'
    })

def logout_user(request):
    request.session.pop('admin_id', None)
    request.session.pop('user_id', None)
    request.session.pop('security_id', None) # Clear security session
    messages.success(request, 'You have been logged out.')
    return redirect('home')


def admin_dashboard(request):
    admin_id=request.session.get('admin_id')

    if not admin_id:
        return redirect('home')

    admin=Admin.objects.get(id=admin_id)

    member_search=request.GET.get('member_search','').strip()

    users=User.objects.all()

    if member_search:
        users=users.filter(
            Q(nick_name__icontains=member_search)|
            Q(flat_no__icontains=member_search)|
            Q(phone__icontains=member_search)|
            Q(dob__icontains=member_search)
        )

    users=users.order_by('nick_name')

    search_query=request.GET.get('pending_search','').strip()

    pending_vehicles=Vehicle.objects.filter(
        is_approved=False,
        is_rejected=False
    ).select_related('user')

    if search_query:
        pending_vehicles=pending_vehicles.filter(
            Q(number__icontains=search_query)|
            Q(user__nick_name__icontains=search_query)|
            Q(user__flat_no__icontains=search_query)|
            Q(user__phone__icontains=search_query)
        )

    pending_vehicles=pending_vehicles.order_by('number')

    security_staff=SecurityStaff.objects.all()

    return render(
        request,
        'admin/admin_dashboard.html',
        {
            'admin':admin,
            'users':users,
            'pending_vehicles':pending_vehicles,
            'pending_search':search_query,
            'member_search':member_search,
            'security_staff':security_staff,
        },
    )


def approve_vehicle(request, vehicle_id):
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return redirect('home')

    if request.method != "POST":
        return redirect('admin_dashboard')

    vehicle = Vehicle.objects.filter(id=vehicle_id).select_related('user').first()
    if not vehicle:
        messages.error(request, 'Vehicle not found.')
        return redirect('admin_dashboard')

    parking_slot = request.POST.get('parking_slot', '').strip().upper()
    if not parking_slot:
        messages.error(request, 'Please allot a parking slot before approving the vehicle.')
        return redirect('admin_dashboard')

    vehicle.is_approved = True
    vehicle.parking_slot = parking_slot
    vehicle.save(update_fields=['is_approved', 'parking_slot'])
    owner_name = vehicle.user.nick_name if vehicle.user else 'Member'
    messages.success(request, f'Approved vehicle {vehicle.number} for {owner_name} and allotted slot {parking_slot}.')
    return redirect('admin_dashboard')


def reject_vehicle(request, vehicle_id):
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return redirect('home')

    if request.method != "POST":
        return redirect('admin_dashboard')

    vehicle = Vehicle.objects.filter(id=vehicle_id).select_related('user').first()

    if not vehicle:
        messages.error(request, 'Vehicle not found.')
        return redirect('admin_dashboard')

    reject_reason = request.POST.get('reject_reason', '').strip()

    if not reject_reason:
        messages.error(request, 'Please provide a reason for rejection.')
        return redirect('admin_dashboard')

    # mark vehicle as rejected
    vehicle.reject_reason = reject_reason
    vehicle.is_rejected = True
    vehicle.save(update_fields=['reject_reason', 'is_rejected'])

    vehicle_number = vehicle.number
    owner_name = vehicle.user.nick_name if vehicle.user else 'Member'

    messages.success(
        request,
        f'Rejected vehicle {vehicle_number} from {owner_name}.'
    )

    return redirect('admin_dashboard')

def add_member(request):
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return redirect('home')

    if request.method != "POST":
        return redirect('admin_dashboard')

    nick_name = request.POST.get('nickname', '').strip()
    phone = request.POST.get('phone', '').strip()
    dob = request.POST.get('dob', '').strip()
    flat_no = request.POST.get('flat_no', '').strip().upper()

    if not nick_name or not phone or not dob or not flat_no:
        messages.error(request, 'All member fields are required.')
        return redirect('admin_dashboard')

    existing_user = User.objects.filter(phone=phone, dob=dob).first()
    if existing_user:
        messages.error(request, 'A member with this phone number and DOB already exists.')
        return redirect('admin_dashboard')

    User.objects.create(
        nick_name=nick_name,
        phone=phone,
        dob=dob,
        flat_no=flat_no,
    )
    messages.success(request, 'Member added successfully.')
    return redirect('admin_dashboard')


def user_dashboard(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')

    user = User.objects.get(id=user_id)
    approved_vehicles = Vehicle.objects.filter(user=user, is_approved=True).order_by('number')
    pending_vehicles = Vehicle.objects.filter(
        user=user,
        is_approved=False,
        is_rejected=False
    ).order_by('number')

    rejected_vehicles = Vehicle.objects.filter(
        user=user,
        is_rejected=True
    ).order_by('number')

    return render(
        request,
        'user/user_dashboard.html',
        {
            'user': user,
            'vehicles': approved_vehicles,
            'pending_vehicles': pending_vehicles,
            'rejected_vehicles': rejected_vehicles,
        },
    )


def add_vehicle(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('home')

    if request.method != "POST":
        return redirect('user_dashboard')

    user = User.objects.get(id=user_id)
    vehicle_number = request.POST.get('vehicle_number', '').strip().upper()
    vehicle_type = request.POST.get('vehicle_type', '').strip()
    rc_book = request.FILES.get('rc_book')
    vehicle_image = request.FILES.get('vehicle_image')
    valid_types = {choice[0] for choice in Vehicle.vehicle_types}

    if not vehicle_number or vehicle_type not in valid_types or not rc_book or not vehicle_image:
        messages.error(request, 'Please provide a valid vehicle number, type, RC book file, and vehicle image.')
        return redirect('user_dashboard')

    existing_vehicle = Vehicle.objects.filter(user=user, number__iexact=vehicle_number).first()
    if existing_vehicle:
        messages.error(request, 'This vehicle is already added to your account.')
        return redirect('user_dashboard')

    # Generate QR code for the vehicle number
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(vehicle_number)
    qr.make(fit=True)
    qr_image = qr.make_image(fill_color="black", back_color="white")

    # Save QR code to in-memory file
    buffer = BytesIO()
    qr_image.save(buffer, format='PNG')
    buffer.seek(0)

    vehicle = Vehicle.objects.create(
        user=user,
        number=vehicle_number,
        type=vehicle_type,
        rc_book=rc_book,
        image=vehicle_image,
    )
    vehicle.qr_code.save(f'qr_{vehicle_number}.png', File(buffer), save=True)

    messages.success(request, 'Vehicle added successfully and is pending community approval.')
    return redirect('user_dashboard')


def create_user(request):
    if request.method == "POST":
        return redirect("home")
    return redirect("home")

def reapply_vehicle(request):

    if request.method == "POST":

        vehicle = Vehicle.objects.get(
            id=request.POST.get("vehicle_id")
        )

        vehicle.number = request.POST.get("vehicle_number")
        vehicle.type = request.POST.get("vehicle_type")

        if request.FILES.get("rc_book"):
            vehicle.rc_book = request.FILES.get("rc_book")

        if request.FILES.get("vehicle_image"):
            vehicle.image = request.FILES.get("vehicle_image")

        # reset approval state
        vehicle.is_approved = False
        vehicle.is_rejected = False
        vehicle.reject_reason = ""

        vehicle.save()

    return redirect("user_dashboard")

def add_security(request):
    if request.method == "POST":
        SecurityStaff.objects.create(

            name=request.POST.get("security_name"),

            phone=request.POST.get("phone"),

            gender=request.POST.get("gender"),

            date_of_birth=request.POST.get("date_of_birth"),

            photo=request.FILES.get("photo")
        )
    return redirect("admin_dashboard")


def delete_security(request, id):
    security = SecurityStaff.objects.get(id=id)
    security.delete()
    return redirect("admin_dashboard")
