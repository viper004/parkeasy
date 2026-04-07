"""
URL configuration for parkease project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.home, name="home"),
    path("create-user/", views.create_user, name="create_user"),
    path("login/", views.login_user, name="login_user"),
    path("create-vehicle/", views.create_vehicle, name="create_vehicle"),
    path("vehicle/<int:vehicle_id>/edit/", views.update_vehicle, name="update_vehicle"),
    path("dashboard/", views.user_dashboard, name="dashboard"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("logout/", views.logout_user, name="logout_user"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
