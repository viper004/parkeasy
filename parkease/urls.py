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
    path('', views.home, name="home"),
    path('login/', views.login_user, name="login_user"),
    path('logout/', views.logout_user, name="logout_user"),
    path('register/', views.create_user, name="create_user"),
    path('admin/dashboard/', views.admin_dashboard, name="admin_dashboard"),
    path('admin/members/add/', views.add_member, name="add_member"),
    path('admin/vehicles/<int:vehicle_id>/approve/', views.approve_vehicle, name="approve_vehicle"),
    path('admin/vehicles/<int:vehicle_id>/reject/', views.reject_vehicle, name="reject_vehicle"),
    path('user/dashboard/', views.user_dashboard, name="user_dashboard"),
    path('user/vehicles/add/', views.add_vehicle, name="add_vehicle"),
    path('reapply-vehicle/',views.reapply_vehicle,name='reapply_vehicle'),
    path('add-security/',views.add_security,name='add_security'),
    path('delete-security/<int:id>/',views.delete_security,name='delete_security'),
    path('security/dashboard/', views.security_dashboard, name="security_dashboard"),
    path('security/gate-control/', views.gate_control, name="gate_control"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
