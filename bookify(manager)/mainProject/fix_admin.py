import os
import sys
import django

# Add project directory to Python path
project_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mainProject')
sys.path.append(project_dir)

try:
    print("Current directory:", os.getcwd())
    print("Project directory:", project_dir)
    print("Setting up Django environment...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainProject.settings')
    django.setup()
    print("Django setup complete.")

    from django.contrib.auth.models import User
    from loginApp.models import UserProfile

    # Check if admin user exists
    admin = User.objects.filter(is_superuser=True).first()
    print(admin.username if admin else "No superuser found")

    # Check and fix admin profile
    if admin:
        profile, created = UserProfile.objects.get_or_create(user=admin)
        if profile.role != 'admin':
            profile.role = 'admin'
            profile.approval_status = 'approved'
            profile.save()
        print(f"Admin profile role: {profile.role}")
        print(f"Admin profile approval status: {profile.approval_status}")
    else:
        print("No admin user found. Create one with python manage.py createsuperuser")
except Exception as e:
    print(f"Error setting up Django environment: {e}")