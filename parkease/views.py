from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import redirect, render

from .decorators import account_login_required, admin_login_required, login_required
from .models import *


def _dashboard_context(request, extra=None):
    user = User.objects.filter(id=request.session.get("user_id")).first()
    vehicles = Vehicle.objects.filter(owner_id=request.session.get("user_id")).order_by("-id")
    apartments = Apartment.objects.order_by("name")
    has_apartment_access = bool(user and user.apartment_id and user.flat_no and user.flat_no != "XXXX")

    context = {
        "user_name": request.session.get("user_name"),
        "user_email": request.session.get("user_email"),
        "user_phone": user.phone if user else "",
        "user_apartment": user.apartment if user else None,
        "user_flat_no": user.flat_no if user and user.flat_no != "XXXX" else "",
        "apartments": apartments,
        "has_apartment_access": has_apartment_access,
        "vehicles": vehicles,
        "vehicle_count": vehicles.count(),
    }
    if extra:
        context.update(extra)
    return context


def _admin_dashboard_context(request, extra=None):
    admin = Admin.objects.filter(id=request.session.get("admin_id")).first()
    apartments = Apartment.objects.filter(owner_id=request.session.get("admin_id")).order_by("-id")

    context = {
        "admin_name": request.session.get("admin_name"),
        "admin_email": request.session.get("admin_email"),
        "apartments": apartments,
        "apartment_count": apartments.count(),
        "admin_record": admin,
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


@login_required
def update_user_apartment(request):
    if request.method != "POST":
        return redirect("dashboard")

    apartment_id = request.POST.get("apartment", "").strip()
    flat_no = request.POST.get("flat_no", "").strip().upper()
    user = User.objects.filter(id=request.session.get("user_id")).first()

    if user is None:
        return redirect("home")

    modal_data = {
        "show_apartment_modal": True,
        "apartment_selection_data": {
            "apartment": apartment_id,
            "flat_no": flat_no,
        },
    }

    apartment = Apartment.objects.filter(id=apartment_id).first()
    if apartment is None or not flat_no:
        context = _dashboard_context(
            request,
            {
                **modal_data,
                "apartment_selection_error": "Select an apartment and enter your flat number.",
            },
        )
        return render(request, "user/dashboard.html", context)

    user.apartment = apartment
    user.flat_no = flat_no
    user.save(update_fields=["apartment", "flat_no"])
    messages.success(request, "Apartment access details saved successfully.")
    return redirect("dashboard")


@admin_login_required
def admin_dashboard(request):
    return render(request, "admin/dashboard.html", _admin_dashboard_context(request))


@admin_login_required
def create_apartment(request):
    if request.method != "POST":
        return redirect("admin_dashboard")

    name = request.POST.get("name", "").strip()
    city = request.POST.get("city", "").strip()

    modal_data = {
        "show_apartment_modal": True,
        "apartment_form_data": {
            "name": name,
            "city": city,
        },
    }

    if not name or not city:
        context = _admin_dashboard_context(
            request,
            {
                **modal_data,
                "apartment_error": "Apartment name and city are required.",
            },
        )
        return render(request, "admin/dashboard.html", context)

    owner = Admin.objects.filter(id=request.session.get("admin_id")).first()
    if owner is None:
        return redirect("home")

    if Apartment.objects.filter(owner=owner).exists():
        context = _admin_dashboard_context(
            request,
            {
                **modal_data,
                "apartment_error": "Each admin can register only one apartment.",
            },
        )
        return render(request, "admin/dashboard.html", context)

    Apartment.objects.create(
        owner=owner,
        name=name,
        city=city,
    )
    messages.success(request, "Apartment registered successfully.")
    return redirect("admin_dashboard")


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

    if not owner.apartment_id or not owner.flat_no or owner.flat_no == "XXXX":
        context = _dashboard_context(
            request,
            {
                **modal_data,
                "vehicle_error": "Select your apartment and enter your flat number before adding a vehicle.",
            },
        )
        return render(request, "user/dashboard.html", context)

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


@account_login_required
def logout_user(request):
    request.session.flush()
    return redirect("home")
