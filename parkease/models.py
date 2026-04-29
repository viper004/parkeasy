from django.db import models

class Admin(models.Model):
    phone = models.CharField(max_length=15, null=False)
    dob = models.CharField(max_length=15, null=False)

class User(models.Model):
    nick_name = models.CharField(max_length=20,null=True)
    phone = models.CharField(max_length=15, null=False)
    dob = models.CharField(max_length=15, null=False)
    flat_no = models.CharField(max_length=10,default="XXX",null=False)

class Vehicle(models.Model):
    vehicle_types=[
        ('2W','Two Wheeler'),
        ('4W','Four Wheeler'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehicles', null=True, blank=True)
    number = models.CharField(max_length=20)
    type= models.CharField(max_length=10,choices=vehicle_types)
    rc_book = models.FileField(upload_to='rc_books/', null=True, blank=True)
    image = models.ImageField(upload_to='vehicles/', null=True, blank=True)
    
