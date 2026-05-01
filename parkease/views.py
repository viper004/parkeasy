from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Q
from django.shortcuts import redirect, render

from .decorators import account_login_required, admin_login_required, login_required
from .models import *

def home(request):
    return render(request,'index.html')


def login_user(request):
    if request.method == "POST":
        phone = request.POST.get('phone')
        dob = request.POST.get('dob')

        # Check if credentials match an Admin
        admin = Admin.objects.filter(phone=phone, dob=dob).first()
        if admin:
            request.session['admin_id'] = admin.id
            return redirect('admin_dashboard')

        # Check if credentials match a User
        user = User.objects.filter(phone=phone, dob=dob).first()
        if user:
            request.session['user_id'] = user.id
            return redirect('user_dashboard')

        # No match found
        messages.error(request, 'Invalid credentials')
        return redirect('home')

    return redirect('home')


def logout_user(request):
    request.session.pop('admin_id', None)
    request.session.pop('user_id', None)
    messages.success(request, 'You have been logged out.')
    return redirect('home')


def admin_dashboard(request):
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return redirect('home')

    admin = Admin.objects.get(id=admin_id)
    users = User.objects.all()
    search_query = request.GET.get('pending_search', '').strip()
    pending_vehicles = Vehicle.objects.filter(is_approved=False).select_related('user')

    if search_query:
        pending_vehicles = pending_vehicles.filter(
            Q(number__icontains=search_query)
            | Q(user__nick_name__icontains=search_query)
            | Q(user__flat_no__icontains=search_query)
            | Q(user__phone__icontains=search_query)
        )

    pending_vehicles = pending_vehicles.order_by('number')
    return render(
        request,
        'admin/admin_dashboard.html',
        {
            'admin': admin,
            'users': users,
            'pending_vehicles': pending_vehicles,
            'pending_search': search_query,
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
    pending_vehicles = Vehicle.objects.filter(user=user, is_approved=False).order_by('number')
    return render(
        request,
        'user/user_dashboard.html',
        {
            'user': user,
            'vehicles': approved_vehicles,
            'pending_vehicles': pending_vehicles,
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

    Vehicle.objects.create(
        user=user,
        number=vehicle_number,
        type=vehicle_type,
        rc_book=rc_book,
        image=vehicle_image,
    )
    messages.success(request, 'Vehicle added successfully and is pending community approval.')
    return redirect('user_dashboard')


def create_user(request):
    if request.method == "POST":
        return redirect("home")
    return redirect("home")
