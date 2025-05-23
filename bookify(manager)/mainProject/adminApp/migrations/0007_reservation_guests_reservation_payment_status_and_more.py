# Generated by Django 4.2.9 on 2025-05-05 21:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('adminApp', '0006_alter_hotel_manager'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='guests',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='reservation',
            name='payment_status',
            field=models.CharField(choices=[('pending', 'Pending'), ('paid', 'Paid'), ('refunded', 'Refunded')], default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='reservation',
            name='special_requests',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='total_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='supportrequest',
            name='assigned_to',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_requests', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='supportrequest',
            name='priority',
            field=models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=20),
        ),
        migrations.AddField(
            model_name='supportrequest',
            name='resolution_notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='supportrequest',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_number', models.CharField(max_length=10)),
                ('room_type', models.CharField(choices=[('standard', 'Standard'), ('deluxe', 'Deluxe'), ('suite', 'Suite'), ('executive', 'Executive'), ('family', 'Family')], max_length=50)),
                ('price_per_night', models.DecimalField(decimal_places=2, max_digits=10)),
                ('capacity', models.PositiveIntegerField(default=2)),
                ('status', models.CharField(choices=[('available', 'Available'), ('occupied', 'Occupied'), ('maintenance', 'Under Maintenance'), ('reserved', 'Reserved')], default='available', max_length=20)),
                ('description', models.TextField(blank=True)),
                ('amenities', models.TextField(blank=True, help_text='Comma-separated list of amenities')),
                ('image_url', models.URLField(blank=True, max_length=500)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rooms', to='adminApp.hotel')),
            ],
            options={
                'unique_together': {('hotel', 'room_number')},
            },
        ),
        migrations.AddField(
            model_name='reservation',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='adminApp.room'),
        ),
        migrations.AddField(
            model_name='supportrequest',
            name='room',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='adminApp.room'),
        ),
    ]
