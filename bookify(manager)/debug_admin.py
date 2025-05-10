import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainProject.settings')
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mainProject'))

try:
    django.setup()
    
    # Import Django models after setup
    from django.contrib.auth.models import User
    from loginApp.models import UserProfile
    
    print('=== Looking for superusers ===')
    admins = User.objects.filter(is_superuser=True)
    print(f'Found {admins.count()} superuser accounts')
    
    for admin in admins:
        print(f'\nSuperuser: {admin.username}')
        print(f'User ID: {admin.id}')
        try:
            profile = UserProfile.objects.get(user=admin)
            print(f'Profile exists with role: {profile.role}')
            print(f'Profile approval status: {profile.approval_status}')
            
            old_role = profile.role
            profile.role = 'admin'
            profile.approval_status = 'approved'
            profile.save()
            print(f'Updated role from {old_role} to: {profile.role}')
            print(f'Updated approval status to: {profile.approval_status}')
        except UserProfile.DoesNotExist:
            print('No profile found, creating one...')
            profile = UserProfile(user=admin, role='admin', approval_status='approved')
            profile.save()
            print('Profile created with role: admin and status: approved')
    
    print('\n=== Looking for all UserProfiles ===')
    profiles = UserProfile.objects.all()
    print(f'Found {profiles.count()} profiles')
    for profile in profiles:
        print(f'Username: {profile.user.username}, Role: {profile.role}, Status: {profile.approval_status}')
    
    print('\n=== Login instructions ===')
    print('When logging in:')
    print('1. Use the exact username of a superuser from the list above')
    print('2. Select the role "admin" from the dropdown')
    print('3. Enter the correct password')
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()

input("\nPress Enter to exit...") 