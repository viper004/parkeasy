from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parkease', '0017_vehicle_is_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='vehicle',
            name='parking_slot',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
