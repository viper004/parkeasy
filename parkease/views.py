from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import redirect, render

from .decorators import admin_login_required, login_required
from .models import Admin, User, Vehicle


def _dashboard_context(request, extra=None):
    user = User.objects.filter(id=request.session.get("user_id")).first()
    vehicles = Vehicle.objects.filter(owner_id=request.session.get("user_id")).order_by("-id")

    context = {
        "user_name": request.session.get("user_name"),
        "user_email": request.session.get("user_email"),
        "user_phone": user.phone if user else "",
        "vehicles": vehicles,
        "vehicle_count": vehicles.count(),
    }
    if extra:
        context.update(extra)
    return context


def _admin_dashboard_context(request, extra=None):
    context = {
        "admin_name": request.session.get("admin_name"),
        "admin_email": request.session.get("admin_email"),
    }
    if extra:
        context.update(extra)
    return context


def _password_matches(raw_password, stored_password):
    if not stored_password:
        return False

    if stored_password.startswith("pbkdf2_"):
        return check_password(raw_password, stored_password)

    return raw_password == stored_password


def home(request):
    if request.session.get("admin_id"):
        return redirect("admin_dashboard")
    if request.session.get("user_id"):
        return redirect("dashboard")
    return render(request, "index.html")


def create_user(request):
    if request.method != "POST":
        return redirect("home")

    name = request.POST.get("name", "").strip()
    email = request.POST.get("email", "").strip()
    phone = request.POST.get("phone", "").strip()
    password = request.POST.get("password", "").strip()

    if not all([name, email, phone, password]):
        return redirect("home")

    User.objects.create(
        name=name,
        email=email,
        phone=phone,
        password=make_password(password),
    )
    return redirect("home")


def login_user(request):
    if request.method != "POST":
        return redirect("home")

    email = request.POST.get("email", "").strip()
    password = request.POST.get("password", "").strip()

    if not email or not password:
        return render(request, "index.html", {"login_error": "Enter email and password."})

    user = User.objects.filter(email=email).first()
    if user and check_password(password, user.password):
        request.session.flush()
        request.session["user_id"] = user.id
        request.session["user_name"] = user.name
        request.session["user_email"] = user.email
        request.session["role"] = "user"
        return redirect("dashboard")

    admin = Admin.objects.filter(email=email).first()
    if admin and _password_matches(password, admin.password):
        request.session.flush()
        request.session["admin_id"] = admin.id
        request.session["admin_name"] = admin.name
        request.session["admin_email"] = admin.email
        request.session["role"] = "admin"
        return redirect("admin_dashboard")

    return render(request, "index.html", {"login_error": "Invalid email or password."})


@login_required
def user_dashboard(request):
    return render(request, "user/dashboard.html", _dashboard_context(request))


@admin_login_required
def admin_dashboard(request):
    return render(request, "admin/dashboard.html", _admin_dashboard_context(request))


@login_required
def create_vehicle(request):
    if request.method != "POST":
        return redirect("dashboard")

    number = request.POST.get("number", "").strip().upper()
    vehicle_type = request.POST.get("type", "").strip()
    image = request.FILES.get("image")

    modal_data = {
        "show_vehicle_modal": True,
        "vehicle_form_data": {
            "number": number,
            "type": vehicle_type,
        },
    }

    if not number or not vehicle_type:
        context = _dashboard_context(
            request,
            {
                **modal_data,
                "vehicle_error": "Vehicle number and type are required.",
            },
        )
        return render(request, "user/dashboard.html", context)

    if Vehicle.objects.filter(number=number).exists():
        context = _dashboard_context(
            request,
            {
                **modal_data,
                "vehicle_error": "That vehicle number is already registered.",
            },
        )
        return render(request, "user/dashboard.html", context)

    owner = User.objects.filter(id=request.session.get("user_id")).first()
    if owner is None:
        return redirect("home")

    Vehicle.objects.create(
        owner=owner,
        number=number,
        type=vehicle_type,
        image=image,
    )
    messages.success(request, "Vehicle added successfully.")
    return redirect("dashboard")


@login_required
def update_vehicle(request, vehicle_id):
    if request.method != "POST":
        return redirect("dashboard")

    owner_id = request.session.get("user_id")
    vehicle = Vehicle.objects.filter(id=vehicle_id, owner_id=owner_id).first()
    if vehicle is None:
        messages.error(request, "Vehicle not found.")
        return redirect("dashboard")

    number = request.POST.get("number", "").strip().upper()
    vehicle_type = request.POST.get("type", "").strip()
    image = request.FILES.get("image")

    edit_modal_data = {
        "show_edit_vehicle_modal": True,
        "edit_vehicle_id": vehicle.id,
        "edit_vehicle_form_data": {
            "id": vehicle.id,
            "number": number,
            "type": vehicle_type,
            "current_image": vehicle.image.url if vehicle.image else "",
        },
    }

    if not number or not vehicle_type:
        context = _dashboard_context(
            request,
            {
                **edit_modal_data,
                "edit_vehicle_error": "Vehicle number and type are required.",
            },
        )
        return render(request, "user/dashboard.html", context)

    if Vehicle.objects.filter(number=number).exclude(id=vehicle.id).exists():
        context = _dashboard_context(
            request,
            {
                **edit_modal_data,
                "edit_vehicle_error": "That vehicle number is already registered.",
            },
        )
        return render(request, "user/dashboard.html", context)

    vehicle.number = number
    vehicle.type = vehicle_type
    if image:
        vehicle.image = image
    vehicle.save()

    messages.success(request, "Vehicle updated successfully.")
    return redirect("dashboard")


@login_required
def logout_user(request):
    request.session.flush()
    return redirect("home")
