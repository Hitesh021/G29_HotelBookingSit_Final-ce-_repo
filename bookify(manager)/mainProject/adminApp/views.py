from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.db.models import Q
from loginApp.models import UserProfile
from .models import Reservation, Hotel, Flight, SupportRequest, Room
from .forms import ReservationForm, HotelForm, FlightForm, RoomForm


# ------------------------- ADMIN DASHBOARD -------------------------
@login_required
def admin_dashboard(request):
    # Check if user is admin
    try:
        profile = UserProfile.objects.get(user=request.user)
        if not profile.is_admin():
            messages.error(request, "You don't have permission to access this page.")
            return redirect('home')
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found.")
        return redirect('login')
    
    # Get counts for dashboard
    hotels_count = Hotel.objects.count()
    users_count = UserProfile.objects.filter(role='customer').count()
    bookings_count = Reservation.objects.count()
    pending_managers_count = UserProfile.objects.filter(role='manager', approval_status='pending').count()
    
    context = {
        'hotels_count': hotels_count,
        'users_count': users_count,
        'bookings_count': bookings_count,
        'pending_managers_count': pending_managers_count,
    }
    
    return render(request, 'adminApp/dashboards/admin_dashboard.html', context)


from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from loginApp.models import UserProfile  # Adjust if your model name or import path is different

# ---------------------------
# Manager Dashboard View
# ---------------------------
@login_required(login_url='/')
def manager_dashboard(request):
    try:
        profile = request.user.profile  # FIX: Use 'profile' not 'userprofile'
        if profile.role != 'manager':
            raise PermissionError
    except (UserProfile.DoesNotExist, PermissionError, AttributeError):
        messages.error(request, "Unauthorized access. You are not a manager.")
        return redirect(reverse('login'))
    
    # Get hotel data for this manager
    try:
        hotel = Hotel.objects.get(name=profile.hotel_name)
    except Hotel.DoesNotExist:
        hotel = None
    
    # Get reservations for this hotel
    if hotel:
        reservations = Reservation.objects.filter(hotel=hotel).order_by('-booking_date')
        total_bookings = reservations.count()
        
        # Get today's check-ins
        today = timezone.now().date()
        todays_checkins = reservations.filter(check_in=today, status='confirmed').count()
        
        # Calculate room occupancy
        total_rooms = hotel.available_rooms + reservations.filter(status='confirmed').count()
        occupied_rooms = reservations.filter(
            check_in__lte=today, 
            check_out__gte=today,
            status='confirmed'
        ).count()
        vacant_rooms = total_rooms - occupied_rooms if total_rooms > occupied_rooms else 0
        
        # Calculate monthly revenue
        first_day_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_reservations = reservations.filter(
            booking_date__gte=first_day_of_month, 
            status='confirmed'
        )
        monthly_revenue = sum(hotel.price_per_night * (r.check_out - r.check_in).days for r in monthly_reservations if r.check_in and r.check_out)
        
        # Get the last 7 days booking data for the chart
        booking_trend_data = []
        for i in range(6, -1, -1):
            day = timezone.now().date() - timezone.timedelta(days=i)
            count = reservations.filter(booking_date__date=day).count()
            booking_trend_data.append(count)
        
        # Get upcoming check-ins
        upcoming_checkins = reservations.filter(
            check_in__gte=today,
            status='confirmed'
        ).order_by('check_in')[:3]
        
        # Get pending support requests
        support_requests = SupportRequest.objects.filter(status='open').order_by('-created_at')[:3]
    else:
        total_bookings = 0
        todays_checkins = 0
        occupied_rooms = 0
        vacant_rooms = 0
        monthly_revenue = 0
        booking_trend_data = [0, 0, 0, 0, 0, 0, 0]
        upcoming_checkins = []
        support_requests = []

    context = {
        'role': profile.role,
        'hotel_name': profile.hotel_name or "Not Assigned",
        'hotel': hotel,
        'total_bookings': total_bookings,
        'todays_checkins': todays_checkins,
        'occupied_rooms': occupied_rooms,
        'vacant_rooms': vacant_rooms,
        'monthly_revenue': monthly_revenue,
        'booking_trend_data': booking_trend_data,
        'upcoming_checkins': upcoming_checkins,
        'support_requests': support_requests
    }
    
    return render(request, 'adminApp/manager_dashboard.html', context)

# ---------------------------
# Customers Page (Manager)
# ---------------------------
@login_required(login_url='/')
def customers_view(request):
    try:
        profile = request.user.profile
        if profile.role != 'manager':
            raise PermissionError
    except (AttributeError, PermissionError):
        messages.error(request, "Unauthorized access.")
        return redirect(reverse('login'))

    # Get hotel data for this manager
    try:
        hotel = Hotel.objects.get(name=profile.hotel_name)
    except Hotel.DoesNotExist:
        hotel = None
    
    if hotel:
        # Get unique customers who have reservations at this hotel
        customer_ids = Reservation.objects.filter(
            hotel=hotel
        ).values_list('user', flat=True).distinct()
        
        customers = UserProfile.objects.filter(
            user_id__in=customer_ids,
            role='customer'
        ).select_related('user')
        
        # Filter by status if provided
        status_filter = request.GET.get('status', '')
        if status_filter:
            # Get reservations with the specified status
            reservation_ids = Reservation.objects.filter(
                hotel=hotel, 
                status=status_filter
            ).values_list('user', flat=True).distinct()
            customers = customers.filter(user_id__in=reservation_ids)
            
        # Search by name if provided
        search_query = request.GET.get('search', '')
        if search_query:
            customers = customers.filter(
                user__username__icontains=search_query
            )
        
        # Get booking stats for each customer
        customer_stats = {}
        for customer in customers:
            customer_reservations = Reservation.objects.filter(
                hotel=hotel,
                user=customer.user
            )
            
            customer_stats[customer.user.id] = {
                'total_bookings': customer_reservations.count(),
                'last_booking': customer_reservations.order_by('-booking_date').first(),
                'total_spent': sum(
                    hotel.price_per_night * (r.check_out - r.check_in).days 
                    for r in customer_reservations.filter(status='confirmed') 
                    if r.check_in and r.check_out
                ),
            }
    else:
        customers = []
        customer_stats = {}
    
    context = {
        'hotel_name': profile.hotel_name,
        'customers': customers,
        'customer_stats': customer_stats,
        'status_filter': status_filter if 'status_filter' in locals() else '',
        'search_query': search_query if 'search_query' in locals() else '',
        'total_customers': len(customers)
    }
    
    return render(request, 'adminApp/customers.html', context)

# ---------------------------
# Reservations Page (Manager)
# ---------------------------
@login_required(login_url='/')
def reservations2_view(request):
    try:
        profile = request.user.profile
        if profile.role != 'manager':
            raise PermissionError
    except (AttributeError, PermissionError):
        messages.error(request, "Unauthorized access.")
        return redirect(reverse('login'))

    # Get hotel data for this manager
    try:
        hotel = Hotel.objects.get(name=profile.hotel_name)
    except Hotel.DoesNotExist:
        hotel = None
    
    # Get reservations for this hotel
    if hotel:
        reservations = Reservation.objects.filter(hotel=hotel).order_by('-booking_date')
        
        # Filter by status if provided
        status_filter = request.GET.get('status', '')
        if status_filter:
            reservations = reservations.filter(status=status_filter)
            
        # Search by customer name
        search_query = request.GET.get('search', '')
        if search_query:
            reservations = reservations.filter(user__username__icontains=search_query)
    else:
        reservations = []
    
    context = {
        'hotel_name': profile.hotel_name,
        'reservations': reservations,
        'status_filter': status_filter if 'status_filter' in locals() else '',
        'search_query': search_query if 'search_query' in locals() else '',
    }
    
    return render(request, 'adminApp/reservation2.html', context)

# ---------------------------
# Rooms Page (Manager)
# ---------------------------
@login_required(login_url='/')
def rooms_view(request):
    try:
        profile = request.user.profile
        if profile.role != 'manager':
            raise PermissionError
    except (AttributeError, PermissionError):
        messages.error(request, "Unauthorized access.")
        return redirect(reverse('login'))

    # Get hotel data for this manager
    try:
        hotel = Hotel.objects.get(name=profile.hotel_name)
    except Hotel.DoesNotExist:
        hotel = None
    
    if hotel:
        rooms = Room.objects.filter(hotel=hotel)
        
        # Filter by status if provided
        status_filter = request.GET.get('status', '')
        if status_filter:
            rooms = rooms.filter(status=status_filter)
            
        # Search by room number or type if provided
        search_query = request.GET.get('search', '')
        if search_query:
            rooms = rooms.filter(
                Q(room_number__icontains=search_query) | 
                Q(room_type__icontains=search_query)
            )
            
        context = {
            'hotel_name': profile.hotel_name,
            'hotel': hotel,
            'rooms': rooms,
            'total_rooms': rooms.count(),
            'available_rooms': rooms.filter(status='available').count(),
            'occupied_rooms': rooms.filter(status='occupied').count(),
            'maintenance_rooms': rooms.filter(status='maintenance').count(),
            'status_filter': status_filter if status_filter else '',
            'search_query': search_query if search_query else '',
        }
    else:
        context = {
            'hotel_name': profile.hotel_name or "Not Assigned",
            'hotel': None,
            'rooms': [],
            'total_rooms': 0,
            'available_rooms': 0,
            'occupied_rooms': 0,
            'maintenance_rooms': 0,
        }
    
    return render(request, 'adminApp/rooms.html', context)

# ---------------------------
# Room CRUD Operations for Managers
# ---------------------------
@login_required(login_url='/')
def room_create(request):
    try:
        profile = request.user.profile
        if profile.role != 'manager':
            raise PermissionError
    except (AttributeError, PermissionError):
        messages.error(request, "Unauthorized access.")
        return redirect(reverse('login'))
    
    # Get hotel data for this manager
    try:
        hotel = Hotel.objects.get(name=profile.hotel_name)
    except Hotel.DoesNotExist:
        messages.error(request, "You don't have a hotel assigned to your account.")
        return redirect(reverse('adminApp:rooms'))
    
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.hotel = hotel
            room.save()
            messages.success(request, f"Room {room.room_number} has been created successfully.")
            return redirect(reverse('adminApp:rooms'))
    else:
        form = RoomForm(initial={'hotel': hotel})
    
    context = {
        'hotel_name': profile.hotel_name,
        'form': form,
        'hotel': hotel,
        'title': 'Add New Room',
        'action': 'Create'
    }
    
    return render(request, 'adminApp/room_form.html', context)

@login_required(login_url='/')
def room_edit(request, room_id):
    try:
        profile = request.user.profile
        if profile.role != 'manager':
            raise PermissionError
    except (AttributeError, PermissionError):
        messages.error(request, "Unauthorized access.")
        return redirect(reverse('login'))
    
    # Get hotel data for this manager
    try:
        hotel = Hotel.objects.get(name=profile.hotel_name)
    except Hotel.DoesNotExist:
        messages.error(request, "You don't have a hotel assigned to your account.")
        return redirect(reverse('adminApp:rooms'))
    
    # Get the room and ensure it belongs to this manager's hotel
    room = get_object_or_404(Room, id=room_id)
    if room.hotel.id != hotel.id:
        messages.error(request, "You don't have permission to edit this room.")
        return redirect(reverse('adminApp:rooms'))
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, f"Room {room.room_number} has been updated successfully.")
            return redirect(reverse('adminApp:rooms'))
    else:
        form = RoomForm(instance=room)
    
    context = {
        'hotel_name': profile.hotel_name,
        'form': form,
        'hotel': hotel,
        'room': room,
        'title': 'Edit Room',
        'action': 'Update'
    }
    
    return render(request, 'adminApp/room_form.html', context)

@login_required(login_url='/')
def room_detail(request, room_id):
    try:
        profile = request.user.profile
        if profile.role != 'manager':
            raise PermissionError
    except (AttributeError, PermissionError):
        messages.error(request, "Unauthorized access.")
        return redirect(reverse('login'))
    
    # Get hotel data for this manager
    try:
        hotel = Hotel.objects.get(name=profile.hotel_name)
    except Hotel.DoesNotExist:
        messages.error(request, "You don't have a hotel assigned to your account.")
        return redirect(reverse('adminApp:rooms'))
    
    # Get the room and ensure it belongs to this manager's hotel
    room = get_object_or_404(Room, id=room_id)
    if room.hotel.id != hotel.id:
        messages.error(request, "You don't have permission to view this room.")
        return redirect(reverse('adminApp:rooms'))
    
    # Get reservations for this room
    reservations = Reservation.objects.filter(room=room).order_by('-booking_date')
    
    context = {
        'hotel_name': profile.hotel_name,
        'hotel': hotel,
        'room': room,
        'reservations': reservations,
        'amenities_list': [amenity.strip() for amenity in room.amenities.split(',')] if room.amenities else []
    }
    
    return render(request, 'adminApp/room_detail.html', context)

@login_required(login_url='/')
def room_delete(request, room_id):
    try:
        profile = request.user.profile
        if profile.role != 'manager':
            raise PermissionError
    except (AttributeError, PermissionError):
        messages.error(request, "Unauthorized access.")
        return redirect(reverse('login'))
    
    # Get hotel data for this manager
    try:
        hotel = Hotel.objects.get(name=profile.hotel_name)
    except Hotel.DoesNotExist:
        messages.error(request, "You don't have a hotel assigned to your account.")
        return redirect(reverse('adminApp:rooms'))
    
    # Get the room and ensure it belongs to this manager's hotel
    room = get_object_or_404(Room, id=room_id)
    if room.hotel.id != hotel.id:
        messages.error(request, "You don't have permission to delete this room.")
        return redirect(reverse('adminApp:rooms'))
    
    if request.method == 'POST':
        # Check if room has active reservations
        active_reservations = Reservation.objects.filter(
            room=room,
            status='confirmed',
        ).exists()
        
        if active_reservations:
            messages.error(request, "Cannot delete room with active reservations.")
            return redirect(reverse('adminApp:room_detail', kwargs={'room_id': room_id}))
        
        room_number = room.room_number
        room.delete()
        messages.success(request, f"Room {room_number} has been deleted successfully.")
        return redirect(reverse('adminApp:rooms'))
    
    context = {
        'hotel_name': profile.hotel_name,
        'hotel': hotel,
        'room': room,
    }
    
    return render(request, 'adminApp/room_confirm_delete.html', context)


# ------------------------- ADMIN: RESERVATIONS VIEW -------------------------
@login_required(login_url='/')
def reservations_view(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. You are not an admin.")
        return redirect(reverse('login'))

    reservations = Reservation.objects.all().order_by('-booking_date')
    return render(request, 'adminApp/dashboards/reservations.html', {
        'reservations': reservations,
    })

def reservation_detail(request, booking_id):
    # Retrieve the reservation using the booking_id
    reservation = get_object_or_404(Reservation, id=booking_id)

    # Pass the reservation object to the template
    return render(request, 'adminApp/reservation_details.html', {
        'reservation': reservation,
    })

def create_reservation(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            # Save the reservation to the database
            form.save()
            # Redirect to the reservations page after saving
            return redirect('adminApp:admin_reservations')
    else:
        form = ReservationForm()

    return render(request, 'adminApp/create_reservation.html', {'form': form})

# ------------------------- ADMIN: USERS TABLE (with search + filter) -------------------------
@login_required(login_url='/')
def user_list_view(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. You are not an admin.")
        return redirect(reverse('login'))

    # Search and role filter
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')

    # Base queryset
    registered_users = UserProfile.objects.select_related('user').all()

    # Apply search
    if search_query:
        registered_users = registered_users.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query)
        )

    # Apply role filter
    if role_filter:
        registered_users = registered_users.filter(role=role_filter)

    # Get active users from session
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    active_user_ids = [
        int(session.get_decoded().get('_auth_user_id'))
        for session in sessions
        if session.get_decoded().get('_auth_user_id') is not None
    ]
    active_users = registered_users.filter(user__id__in=active_user_ids)

    context = {
        'registered_users': registered_users,
        'active_users': active_users,
        'search_query': search_query,
        'role_filter': role_filter,
    }

    return render(request, 'adminApp/dashboards/users.html', context)


# ------------------------- ADMIN: SINGLE USER DETAIL -------------------------
@login_required(login_url='/')
def user_detail_view(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. You are not an admin.")
        return redirect('adminApp:user_list_view')

    user_profile = get_object_or_404(UserProfile, user__id=user_id)

    return render(request, 'adminApp/dashboards/user_detail.html', {
        'profile': user_profile
    })


# ------------------------- ADMIN: HOTELS & FLIGHTS VIEW -------------------------
@login_required(login_url='/')
def HNF_view(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. You are not an admin.")
        return redirect(reverse('login'))
        
    hotels = Hotel.objects.all().order_by('name')
    flights = Flight.objects.all().order_by('departure_time')
    
    return render(request, 'adminApp/dashboards/hotelsNflights.html', {
        'hotels': hotels,
        'flights': flights
    })

# ------------------------- HOTEL CRUD OPERATIONS -------------------------
@login_required(login_url='/')
def hotel_list(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. You are not an admin.")
        return redirect(reverse('login'))
        
    hotels = Hotel.objects.all().order_by('name')
    return render(request, 'adminApp/dashboards/hotel_list.html', {'hotels': hotels})

@login_required(login_url='/')
def hotel_create(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. You are not an admin.")
        return redirect(reverse('login'))
        
    if request.method == 'POST':
        form = HotelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Hotel successfully created.")
            return redirect('adminApp:HNF')
    else:
        form = HotelForm()
        
    return render(request, 'adminApp/dashboards/hotel_form.html', {
        'form': form,
        'title': 'Add New Hotel'
    })

@login_required(login_url='/')
def hotel_edit(request, hotel_id):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. You are not an admin.")
        return redirect(reverse('login'))
        
    hotel = get_object_or_404(Hotel, id=hotel_id)
    
    if request.method == 'POST':
        form = HotelForm(request.POST, instance=hotel)
        if form.is_valid():
            form.save()
            messages.success(request, "Hotel successfully updated.")
            return redirect('adminApp:HNF')
    else:
        form = HotelForm(instance=hotel)
        
    return render(request, 'adminApp/dashboards/hotel_form.html', {
        'form': form,
        'hotel': hotel,
        'title': 'Edit Hotel'
    })

@login_required(login_url='/')
def hotel_delete(request, hotel_id):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. You are not an admin.")
        return redirect(reverse('login'))
        
    hotel = get_object_or_404(Hotel, id=hotel_id)
    
    if request.method == 'POST':
        hotel.delete()
        messages.success(request, "Hotel successfully deleted.")
        return redirect('adminApp:HNF')
        
    return render(request, 'adminApp/dashboards/hotel_confirm_delete.html', {
        'hotel': hotel
    })

# ------------------------- FLIGHT CRUD OPERATIONS -------------------------
@login_required(login_url='/')
def flight_list(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. You are not an admin.")
        return redirect(reverse('login'))
        
    flights = Flight.objects.all().order_by('departure_time')
    return render(request, 'adminApp/dashboards/flight_list.html', {'flights': flights})

@login_required(login_url='/')
def flight_create(request):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. You are not an admin.")
        return redirect(reverse('login'))
        
    if request.method == 'POST':
        form = FlightForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Flight successfully created.")
            return redirect('adminApp:HNF')
    else:
        form = FlightForm()
        
    return render(request, 'adminApp/dashboards/flight_form.html', {
        'form': form,
        'title': 'Add New Flight'
    })

@login_required(login_url='/')
def flight_edit(request, flight_id):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. You are not an admin.")
        return redirect(reverse('login'))
        
    flight = get_object_or_404(Flight, id=flight_id)
    
    if request.method == 'POST':
        form = FlightForm(request.POST, instance=flight)
        if form.is_valid():
            form.save()
            messages.success(request, "Flight successfully updated.")
            return redirect('adminApp:HNF')
    else:
        form = FlightForm(instance=flight)
        
    return render(request, 'adminApp/dashboards/flight_form.html', {
        'form': form,
        'flight': flight,
        'title': 'Edit Flight'
    })

@login_required(login_url='/')
def flight_delete(request, flight_id):
    if not request.user.is_superuser:
        messages.error(request, "Access denied. You are not an admin.")
        return redirect(reverse('login'))
        
    flight = get_object_or_404(Flight, id=flight_id)
    
    if request.method == 'POST':
        flight.delete()
        messages.success(request, "Flight successfully deleted.")
        return redirect('adminApp:HNF')
        
    return render(request, 'adminApp/dashboards/flight_confirm_delete.html', {
        'flight': flight
    })

# ------------------------
# Manager Approval Views
# ------------------------
@login_required
def pending_managers_view(request):
    """Display all pending manager applications for admin approval"""
    # Check if user is admin
    profile = UserProfile.objects.get(user=request.user)
    if not profile.is_admin():
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    # Get all pending manager applications
    pending_managers = UserProfile.objects.filter(
        role='manager',
        approval_status='pending'
    ).select_related('user')
    
    context = {
        'pending_managers': pending_managers,
    }
    
    return render(request, 'adminApp/pending_managers.html', context)

@login_required
def approve_manager(request, user_id):
    """Approve a pending manager application"""
    # Check if user is admin
    profile = UserProfile.objects.get(user=request.user)
    if not profile.is_admin():
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('home')
    
    # Get the manager profile
    manager_profile = get_object_or_404(UserProfile, user_id=user_id, role='manager', approval_status='pending')
    
    # Extract city from address if it exists
    try:
        city_name = manager_profile.hotel_city
        if not city_name and ',' in manager_profile.hotel_address:
            city_name = manager_profile.hotel_address.split(',')[-2].strip()
    except:
        city_name = "Unknown"
    
    # Generate a unique hotel ID
    hotel_id = f"HT-{timezone.now().strftime('%Y%m%d')}-{manager_profile.user.id}"
    
    # Pre-populate the form with manager data
    initial_data = {
        'name': manager_profile.hotel_name,
        'location': manager_profile.hotel_address,
        'manager': manager_profile.user,
        'description': manager_profile.hotel_description,
        'hotel_id': hotel_id,
        'address_line': manager_profile.hotel_address,
        'city_name': manager_profile.hotel_city or city_name,
        'country_code': manager_profile.hotel_country or 'USA',
        'postal_code': manager_profile.hotel_postal_code or '',
        'iata_code': manager_profile.hotel_iata_code or '',
        'rating': manager_profile.hotel_rating or 3,
        'image_url': manager_profile.hotel_image_url or '',
        'price_per_night': 100.00,  # Default
        'available_rooms': 10,  # Default
        'status': 'active'
    }
    
    if request.method == 'POST':
        form = HotelForm(request.POST)
        if form.is_valid():
            # Save the hotel
            hotel = form.save()
            
            # Update manager status to approved
            manager_profile.approval_status = 'approved'
            manager_profile.approval_date = timezone.now()
            manager_profile.save()
            
            messages.success(request, f"Manager for {manager_profile.hotel_name} has been approved successfully. Hotel has been created.")
            return redirect('adminApp:pending_managers')
    else:
        form = HotelForm(initial=initial_data)
    
    context = {
        'manager_profile': manager_profile,
        'form': form
    }
    
    return render(request, 'adminApp/approve_manager_with_hotel_form.html', context)

@login_required
def reject_manager(request, user_id):
    """Reject a pending manager application"""
    # Check if user is admin
    profile = UserProfile.objects.get(user=request.user)
    if not profile.is_admin():
        messages.error(request, "You don't have permission to perform this action.")
        return redirect('home')
    
    # Get the manager profile
    manager_profile = get_object_or_404(UserProfile, user_id=user_id, role='manager', approval_status='pending')
    
    if request.method == 'POST':
        # Get rejection reason
        rejection_reason = request.POST.get('rejection_reason', '')
        
        # Update manager status to rejected
        manager_profile.approval_status = 'rejected'
        manager_profile.rejection_reason = rejection_reason
        manager_profile.save()
        
        messages.success(request, f"Manager application for {manager_profile.hotel_name} has been rejected.")
        return redirect('adminApp:pending_managers')
    
    context = {
        'manager_profile': manager_profile
    }
    
    return render(request, 'adminApp/reject_manager.html', context)

@login_required
def manager_details(request, user_id):
    """View details of a manager application"""
    # Check if user is admin
    profile = UserProfile.objects.get(user=request.user)
    if not profile.is_admin():
        messages.error(request, "You don't have permission to view this page.")
        return redirect('home')
    
    # Get the manager profile
    manager_profile = get_object_or_404(UserProfile, user_id=user_id, role='manager')
    
    context = {
        'manager_profile': manager_profile
    }
    
    return render(request, 'adminApp/manager_details.html', context)