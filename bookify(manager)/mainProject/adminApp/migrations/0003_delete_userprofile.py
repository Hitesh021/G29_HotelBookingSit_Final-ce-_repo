# Generated by Django 5.2 on 2025-04-10 20:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('adminApp', '0002_alter_userprofile_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
