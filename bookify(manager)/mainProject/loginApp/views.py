from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse
from loginApp.models import UserProfile
from django.contrib.auth import logout
from django.utils import timezone

# -------------------- LOGIN VIEW --------------------
@csrf_protect
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        selected_role = request.POST.get('role', '').strip().lower()
        hotel_name_input = request.POST.get('hotel_name', '').strip()

        user = authenticate(request, username=username, password=password)

        if user:
            profile, created = UserProfile.objects.get_or_create(user=user)

            if created and user.is_superuser:
                profile.role = 'admin'
                profile.save()

            actual_role = (profile.role or '').strip().lower()

            if not actual_role:
                messages.error(request, "You're a pre-registered user without a role. Please contact admin.")
                return redirect(reverse('login'))

            if actual_role != selected_role:
                messages.error(request, f"You are not assigned the role '{selected_role}'.")
                return redirect(reverse('login'))

            if selected_role == 'admin' and not user.is_superuser:
                messages.error(request, "Access denied. You are not an admin.")
                return redirect(reverse('login'))

            if selected_role == 'manager':
                if not hotel_name_input:
                    messages.error(request, "Hotel name is required for manager login.")
                    return redirect(reverse('login'))
                if not profile.hotel_name or profile.hotel_name.strip().lower() != hotel_name_input.lower():
                    messages.error(request, f"No hotel named '{hotel_name_input}' associated with this manager.")
                    return redirect(reverse('login'))
                
                # Check if manager is approved
                if profile.approval_status == 'pending':
                    login(request, user)
                    request.session.set_expiry(0)  # session ends when browser closes
                    request.session['role'] = actual_role
                    messages.warning(request, "Your manager account is pending approval by an administrator.")
                    return redirect(reverse('manager_pending'))
                
                if profile.approval_status == 'rejected':
                    login(request, user)
                    request.session.set_expiry(0)  # session ends when browser closes
                    request.session['role'] = actual_role
                    messages.error(request, f"Your manager account has been rejected. Reason: {profile.rejection_reason or 'No reason provided.'}")
                    return redirect(reverse('manager_rejected'))

            login(request, user)
            request.session.set_expiry(0)  # session ends when browser closes
            request.session['role'] = actual_role

            if actual_role == 'admin':
                return redirect(reverse('adminApp:admin_dashboard'))
            elif actual_role == 'manager':
                return redirect(reverse('adminApp:manager_dashboard'))
            elif actual_role == 'customer':
                return redirect(reverse('home'))  # Redirect to home for customers
            else:
                messages.error(request, "Invalid role assigned.")
                return redirect(reverse('login'))

        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'loginApp/login.html')


# -------------------- REGISTER VIEW --------------------
@csrf_protect
def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        selected_role = request.POST.get('role', '').strip().lower()
        
        # Get basic hotel details for managers
        hotel_name_input = request.POST.get('hotel_name', '').strip()
        
        # Additional hotel details
        hotel_address = request.POST.get('hotel_address', '').strip()
        hotel_city = request.POST.get('hotel_city', '').strip()
        hotel_state = request.POST.get('hotel_state', '').strip()
        hotel_postal_code = request.POST.get('hotel_postal_code', '').strip()
        hotel_country = request.POST.get('hotel_country', '').strip()
        hotel_contact_phone = request.POST.get('hotel_contact_phone', '').strip()
        hotel_contact_email = request.POST.get('hotel_contact_email', '').strip()
        hotel_description = request.POST.get('hotel_description', '').strip()
        hotel_rating = request.POST.get('hotel_rating', '').strip()
        hotel_image_url = request.POST.get('hotel_image_url', '').strip()
        hotel_iata_code = request.POST.get('hotel_iata_code', '').strip()
        
        # Format the full address (without state/postal code since they're optional now)
        full_address = f"{hotel_address}, {hotel_city}, {hotel_country}"

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect(reverse('register'))

        if selected_role not in ['customer', 'manager']:
            messages.error(request, "Invalid role selected. Only 'customer' or 'manager' allowed.")
            return redirect(reverse('register'))

        if get_user_model().objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose a different one.")
            return redirect(reverse('register'))
            
        # Validate hotel details for managers
        if selected_role == 'manager':
            if not hotel_name_input:
                messages.error(request, "Hotel name is required for managers.")
                return redirect(reverse('register'))
                
            # Check if hotel name is unique among approved managers
            existing_hotel = UserProfile.objects.filter(
                hotel_name__iexact=hotel_name_input,
                role='manager',
                approval_status='approved'
            ).exists()
            
            if existing_hotel:
                messages.error(request, f"A manager for hotel '{hotel_name_input}' already exists.")
                return redirect(reverse('register'))
                
            # Check required fields for hotel managers
            if not hotel_address:
                messages.error(request, "Hotel address is required for managers.")
                return redirect(reverse('register'))
                
            if not hotel_city:
                messages.error(request, "Hotel city is required for managers.")
                return redirect(reverse('register'))
                
            # Remove the state validation since it's not in the form anymore
            # if not hotel_state:
            #     messages.error(request, "Hotel state/province is required for managers.")
            #     return redirect(reverse('register'))
            
            if not hotel_iata_code:
                messages.error(request, "IATA code is required for managers.")
                return redirect(reverse('register'))
                
            if not hotel_contact_phone:
                messages.error(request, "Contact phone is required for managers.")
                return redirect(reverse('register'))

        user = get_user_model().objects.create_user(username=username, password=password)

        # Create or update profile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = selected_role
        
        # Set approval status based on role
        if selected_role == 'manager':
            profile.approval_status = 'pending'
            profile.hotel_name = hotel_name_input
            profile.hotel_address = full_address
            profile.hotel_description = hotel_description
            profile.hotel_contact_phone = hotel_contact_phone
            
            # Save additional hotel details
            profile.hotel_city = hotel_city
            profile.hotel_state = hotel_state  # Keep storing it even if optional
            profile.hotel_postal_code = hotel_postal_code  # Keep storing it even if optional
            profile.hotel_country = hotel_country
            profile.hotel_contact_email = hotel_contact_email
            profile.hotel_rating = hotel_rating
            profile.hotel_image_url = hotel_image_url
            profile.hotel_iata_code = hotel_iata_code  # Store the new IATA code field
            
            messages.success(request, "Registration successful! Your manager account is pending approval by an administrator.")
        else:
            profile.approval_status = 'approved'
            messages.success(request, "Registration successful! Please log in.")
            
        profile.save()
        
        # Redirect to login
        return redirect(reverse('login'))

    return render(request, 'loginApp/register.html')

# -------------------- MANAGER STATUS VIEWS --------------------

def manager_pending_view(request):
    """View for managers with pending approval status"""
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
        
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'manager' or profile.approval_status != 'pending':
        return redirect(reverse('home'))
        
    return render(request, 'loginApp/manager_pending.html')
    
def manager_rejected_view(request):
    """View for managers with rejected approval status"""
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
        
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'manager' or profile.approval_status != 'rejected':
        return redirect(reverse('home'))
        
    context = {
        'rejection_reason': profile.rejection_reason or 'No reason provided'
    }
    return render(request, 'loginApp/manager_rejected.html', context)

def manager_reapply_view(request):
    """View for rejected managers to update their application and reapply"""
    if not request.user.is_authenticated:
        return redirect(reverse('login'))
        
    profile = UserProfile.objects.get(user=request.user)
    if profile.role != 'manager' or profile.approval_status != 'rejected':
        return redirect(reverse('home'))
    
    if request.method == "POST":
        # Get updated hotel details
        hotel_name = request.POST.get('hotel_name', '').strip()
        hotel_address = request.POST.get('hotel_address', '').strip()
        hotel_description = request.POST.get('hotel_description', '').strip()
        hotel_contact_phone = request.POST.get('hotel_contact_phone', '').strip()
        confirm_changes = request.POST.get('confirm_changes') == 'on'
        
        # Validate inputs
        if not hotel_name:
            messages.error(request, "Hotel name is required.")
            return redirect(reverse('manager_reapply'))
            
        if not hotel_address:
            messages.error(request, "Hotel address is required.")
            return redirect(reverse('manager_reapply'))
            
        if not hotel_contact_phone:
            messages.error(request, "Contact phone is required.")
            return redirect(reverse('manager_reapply'))
            
        if not confirm_changes:
            messages.error(request, "You must confirm your changes.")
            return redirect(reverse('manager_reapply'))
        
        # Check if hotel name is unique among approved managers (excluding the current user)
        existing_hotel = UserProfile.objects.filter(
            hotel_name__iexact=hotel_name,
            role='manager',
            approval_status='approved'
        ).exclude(user=request.user).exists()
        
        if existing_hotel:
            messages.error(request, f"A manager for hotel '{hotel_name}' already exists. Please choose a different name.")
            return redirect(reverse('manager_reapply'))
        
        # Update profile with new information
        profile.hotel_name = hotel_name
        profile.hotel_address = hotel_address
        profile.hotel_description = hotel_description
        profile.hotel_contact_phone = hotel_contact_phone
        profile.approval_status = 'pending'  # Change status back to pending
        profile.rejection_reason = None  # Clear the rejection reason
        profile.save()
        
        messages.success(request, "Your application has been updated and resubmitted for approval.")
        return redirect(reverse('manager_pending'))
    
    # If GET request, display the form
    context = {
        'profile': profile,
        'rejection_reason': profile.rejection_reason or 'No reason provided'
    }
    return render(request, 'loginApp/manager_reapply.html', context)

# -------------------- LOGOUT VIEW --------------------

def logout_view(request):
    # Log the user out
    logout(request)
    
    # Redirect to the home page after logout
    return redirect('home')  # Replace 'home' with the name of your home page URL pattern if it's different



# -------------------- CSRF FAILURE VIEW --------------------
def csrf_failure(request, reason=""):
    return render(request, 'loginApp/errors/403.html', status=403)
