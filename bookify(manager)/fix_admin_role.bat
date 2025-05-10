@echo off
echo Fixing admin user role...
cd mainProject
python -c "from django.contrib.auth.models import User; from loginApp.models import UserProfile; admin = User.objects.filter(is_superuser=True).first(); print(f'Admin user found: {admin.username}' if admin else 'No admin user found'); profile, created = UserProfile.objects.get_or_create(user=admin); profile.role = 'admin'; profile.approval_status = 'approved'; profile.save(); print(f'Updated role to: {profile.role}'); print(f'Updated approval status to: {profile.approval_status}')"
echo Admin role fix attempt completed.
pause
