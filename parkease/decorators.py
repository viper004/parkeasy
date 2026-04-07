from functools import wraps

from django.shortcuts import redirect


def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.session.get("user_id"):
            return redirect("home")
        return view_func(request, *args, **kwargs)

    return wrapped_view


def admin_login_required(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.session.get("admin_id"):
            return redirect("home")
        return view_func(request, *args, **kwargs)

    return wrapped_view
