from django.db import models

class Admin(models.Model):
    name = models.CharField(max_length=25)
    email = models.EmailField()
    password = models.CharField(max_length=128)

class Apartment(models.Model):
    owner = models.ForeignKey(Admin,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)


class User(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    apartment = models.ForeignKey(Apartment,on_delete=models.CASCADE,null=True)
    flat_no = models.CharField(max_length=50,default="XXXX")
    created_at = models.DateTimeField(auto_now_add=True)

class Vehicle(models.Model):

    VEHICLE_TYPE_CHOICES = (
        ('bike', 'Bike'),
        ('car', 'Car'),
        ('scooter', 'Scooter'),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    number = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES)
    is_parked = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    image = models.FileField(upload_to='vehicles/', blank=True, null=True)

    def __str__(self):
        return self.number

    def save(self, *args, **kwargs):
        if self.number:
            self.number = self.number.upper()
        super().save(*args, **kwargs)
