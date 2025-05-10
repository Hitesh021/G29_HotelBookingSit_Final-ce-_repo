import os
import sys
import django
import getpass

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mainProject.settings')
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mainProject'))

try:
    django.setup()
    
    # Import Django models after setup
    from django.contrib.auth.models import User
    from loginApp.models import UserProfile
    
    print('=== Create New Admin User ===')
    
    # Get user input
    username = input("Enter new admin username: ")
    email = input("Enter email (optional): ")
    password = getpass.getpass("Enter password: ")
    confirm_password = getpass.getpass("Confirm password: ")
    
    if password != confirm_password:
        print("Passwords don't match!")
        sys.exit(1)
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists!")
        sys.exit(1)
    
    # Create superuser
    print(f"Creating superuser '{username}'...")
    admin = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    
    # Create profile with admin role
    profile = UserProfile(
        user=admin,
        role='admin',
        approval_status='approved'
    )
    profile.save()
    
    print(f"\nAdmin user '{username}' created successfully with role 'admin'!")
    print("\nTo login:")
    print(f"1. Username: {username}")
    print("2. Select role: admin")
    print("3. Enter the password you just created")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()

input("\nPress Enter to exit...") 