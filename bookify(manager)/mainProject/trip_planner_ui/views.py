from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import requests
import json
from datetime import datetime, timedelta
import logging
from decimal import Decimal
from loginApp.models import UserActivity
from app1.models import CartItem, FlightCartItem  # Use existing cart models instead

# Configure logger
logger = logging.getLogger(__name__)

# Flask API base URL
TRIP_PLANNER_API_URL = getattr(settings, 'TRIP_PLANNER_API_URL', 'http://localhost:5000')

@login_required(login_url='/login/')
def trip_planner_home(request):
    """Render the trip planner home/search page"""
    # Default dates (tomorrow and a week later)
    tomorrow = datetime.today() + timedelta(days=1)
    next_week = tomorrow + timedelta(days=7)
    
    context = {
        'departure_date': tomorrow.strftime('%Y-%m-%d'),
        'return_date': next_week.strftime('%Y-%m-%d'),
    }
    
    return render(request, 'trip_planner_ui/trip_planner_home.html', context)

def trip_planner_search(request):
    """Handle trip planner search form submission"""
    if request.method == 'POST':
        # Extract search parameters
        origin = request.POST.get('origin', '')
        destination = request.POST.get('destination', '')
        departure_date = request.POST.get('departure_date', '')
        return_date = request.POST.get('return_date', '')
        adults = int(request.POST.get('adults', 1))
        
        # Store search parameters in session
        request.session['trip_search_params'] = {
            'origin': origin,
            'destination': destination,
            'departure_date': departure_date,
            'return_date': return_date,
            'adults': adults,
        }
        
        # Log user activity if they performed a search and are logged in
        if request.user.is_authenticated:
            activity_title = f"Trip search from {origin} to {destination}"
            activity_description = f"Searched for trip from {origin} to {destination} departing on {departure_date} and returning on {return_date} for {adults} adults"
            
            UserActivity.objects.create(
                user=request.user,
                activity_type='search_trip',
                title=activity_title,
                description=activity_description
            )
        
        # Redirect to results page (which will make the API call)
        return redirect('trips:results')
        
    # If not POST, redirect to the search form
    return redirect('trips:home')

def trip_planner_results(request):
    """Display trip planner search results"""
    # Get search parameters from session
    search_params = request.session.get('trip_search_params', {})
    
    # If no search parameters, redirect to search form
    if not search_params:
        messages.error(request, "Please enter search criteria for your trip.")
        return redirect('trips:home')
        
    try:
        # Call Flask API to get trip options
        api_url = f"{TRIP_PLANNER_API_URL}/api/trip/search"
        
        # API expects JSON data
        headers = {'Content-Type': 'application/json'}
        
        # Make the API request
        response = requests.post(
            api_url, 
            json=search_params,  # Will be converted to JSON
            headers=headers,
            timeout=60  # 60 second timeout
        )
        
        if response.status_code == 200:
            # Parse JSON response
            data = response.json()
            trip_options = data.get('trip_options', [])
            
            # Prepare context for template
            context = {
                'search_params': search_params,
                'trip_options': trip_options,
                'trip_count': len(trip_options),
                'error': None
            }
        else:
            # API returned an error status
            error_message = f"Error from Trip Planner API: {response.status_code}"
            try:
                # Try to extract error message from JSON response
                error_data = response.json()
                if 'error' in error_data:
                    error_message = error_data['error']
            except:
                pass
            
            logger.error(f"API error: {error_message}")
            context = {
                'search_params': search_params,
                'trip_options': [],
                'trip_count': 0,
                'error': error_message
            }
    
    except requests.exceptions.RequestException as e:
        # Connection error or timeout
        logger.error(f"Request error: {str(e)}")
        context = {
            'search_params': search_params,
            'trip_options': [],
            'trip_count': 0,
            'error': f"Failed to connect to Trip Planner service. Please try again later. ({str(e)})"
        }
    
    except Exception as e:
        # Any other exception
        logger.error(f"Unexpected error: {str(e)}")
        context = {
            'search_params': search_params,
            'trip_options': [],
            'trip_count': 0,
            'error': "An unexpected error occurred. Please try again."
        }
    
    return render(request, 'trip_planner_ui/trip_planner_results.html', context)

def trip_details(request, trip_id):
    """Display detailed information for a specific trip option"""
    # Get search parameters from session
    search_params = request.session.get('trip_search_params', {})
    
    # If no search parameters, redirect to search form
    if not search_params:
        messages.error(request, "Please start a new trip search.")
        return redirect('trips:home')
    
    # Extract trip ID components
    # Expected format: trip-{flight_id}-{hotel_id}
    try:
        parts = trip_id.split('-')
        flight_id = parts[1]
        hotel_id = parts[2]
        
        # We would typically call the API to get detailed information
        # For now, we'll use placeholder data
        trip_details = {
            'id': trip_id,
            'flight': {
                'id': flight_id,
                'carrier': 'Sample Airline',
                'departure_time': '08:00',
                'arrival_time': '10:30',
                'price': 299.99,
                'origin': search_params.get('origin'),
                'destination': search_params.get('destination'),
                'departure_date': search_params.get('departure_date'),
                'return_date': search_params.get('return_date'),
            },
            'hotel': {
                'id': hotel_id,
                'name': 'Sample Hotel',
                'rating': 4.5,
                'address': '123 Main St, Sample City',
                'price_per_night': 129.99,
                'check_in': search_params.get('departure_date'),
                'check_out': search_params.get('return_date'),
                'amenities': ['WiFi', 'Pool', 'Breakfast']
            },
            'total_price': 689.95,
            'nights': 3,
            'adults': search_params.get('adults', 1)
        }
        
        context = {
            'trip_details': trip_details,
            'error': None
        }
        
    except Exception as e:
        # Any error in processing
        logger.error(f"Error processing trip details: {str(e)}")
        context = {
            'trip_details': None,
            'error': "Failed to load trip details. Please try again."
        }
    
    return render(request, 'trip_planner_ui/trip_details.html', context)

# New view for individual flight details
@login_required
def flight_item_details_view(request, flight_id):
    """Display detailed information for a specific flight option from Flask API"""
    api_url = f"{TRIP_PLANNER_API_URL}/api/flight/details/{flight_id}"
    context = {
        'flight_id': flight_id,
        'flight_details': None,
        'error': None
    }
    try:
        response = requests.get(api_url, timeout=30)
        if response.status_code == 200:
            context['flight_details'] = response.json()
        else:
            error_message = f"Error from API: {response.status_code}"
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_message = error_data['error']
            except:
                pass # Keep the status code error
            context['error'] = error_message
            logger.error(f"API error fetching flight details for {flight_id}: {error_message} - URL: {api_url}")

    except requests.exceptions.RequestException as e:
        context['error'] = f"Could not connect to the details service: {str(e)}"
        logger.error(f"RequestException fetching flight details for {flight_id}: {str(e)} - URL: {api_url}")
    
    return render(request, 'trip_planner_ui/flight_detail_page.html', context)

# New view for individual hotel details
@login_required
def hotel_item_details_view(request, hotel_id):
    """Display detailed information for a specific hotel option from Flask API"""
    api_url = f"{TRIP_PLANNER_API_URL}/api/hotel/details/{hotel_id}"
    context = {
        'hotel_id': hotel_id,
        'hotel_details': None,
        'error': None
    }
    try:
        response = requests.get(api_url, timeout=30)
        if response.status_code == 200:
            context['hotel_details'] = response.json()
        else:
            error_message = f"Error from API: {response.status_code}"
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_message = error_data['error']
            except:
                pass # Keep the status code error
            context['error'] = error_message
            logger.error(f"API error fetching hotel details for {hotel_id}: {error_message} - URL: {api_url}")
            
    except requests.exceptions.RequestException as e:
        context['error'] = f"Could not connect to the details service: {str(e)}"
        logger.error(f"RequestException fetching hotel details for {hotel_id}: {str(e)} - URL: {api_url}")

    return render(request, 'trip_planner_ui/hotel_detail_page.html', context)

@login_required
def add_package_to_cart(request):
    if request.method == 'POST':
        try:
            package_unique_id = request.POST.get('package_id')
            total_package_price = request.POST.get('total_package_price')
            adults = request.POST.get('adults')
            
            search_departure_date = request.POST.get('search_departure_date')
            search_return_date = request.POST.get('search_return_date')

            flight_data_json = request.POST.get('flight_data', 'null') # Get as string, default to 'null'
            hotel_data_json = request.POST.get('hotel_data', 'null')   # Get as string, default to 'null'

            flight_data = json.loads(flight_data_json) if flight_data_json != 'null' else None
            hotel_data = json.loads(hotel_data_json) if hotel_data_json != 'null' else None

            # Basic validation
            if not all([package_unique_id, total_package_price, adults, search_departure_date, search_return_date]):
                messages.error(request, "Incomplete package data. Could not add to cart.")
                return redirect(request.META.get('HTTP_REFERER', 'trips:home'))

            # Add flight to FlightCartItem
            if flight_data:
                try:
                    departure_datetime = datetime.strptime(
                        flight_data.get('departure_datetime', search_departure_date), 
                        '%Y-%m-%dT%H:%M:%S' if 'T' in flight_data.get('departure_datetime', '') else '%Y-%m-%d'
                    )
                    
                    return_datetime = None
                    if flight_data.get('return_departure_datetime'):
                        return_datetime = datetime.strptime(
                            flight_data.get('return_departure_datetime', search_return_date),
                            '%Y-%m-%dT%H:%M:%S' if 'T' in flight_data.get('return_departure_datetime', '') else '%Y-%m-%d'
                        )
                    
                    # Create FlightCartItem
                    flight_cart_item = FlightCartItem(
                        user=request.user,
                        offer_id=flight_data.get('id', f"package-flight-{package_unique_id}"),
                        origin=flight_data.get('origin', ''),
                        destination=flight_data.get('destination', ''),
                        departure_date=departure_datetime,
                        return_date=return_datetime,
                        airline=flight_data.get('carrier', 'Package Flight'),
                        flight_number=flight_data.get('flight_number', ''),
                        price=Decimal(flight_data.get('price', 0)),
                        passengers=int(adults),
                        flight_class=flight_data.get('cabin_class', 'ECONOMY'),
                        is_round_trip=return_datetime is not None
                    )
                    flight_cart_item.save()
                    
                    logger.info(f"Added flight to cart: {flight_data.get('id')}")
                except Exception as e:
                    logger.error(f"Error adding flight to cart: {str(e)}")
                    messages.warning(request, f"Could not add flight to cart: {str(e)}")
            
            # Add hotel to CartItem
            if hotel_data:
                try:
                    check_in_date = datetime.strptime(
                        hotel_data.get('check_in_date', search_departure_date), 
                        '%Y-%m-%d'
                    ).date()
                    
                    check_out_date = datetime.strptime(
                        hotel_data.get('check_out_date', search_return_date), 
                        '%Y-%m-%d'
                    ).date()
                    
                    # Create CartItem for hotel
                    hotel_cart_item = CartItem(
                        user=request.user,
                        hotel_name=hotel_data.get('name', 'Package Hotel'),
                        hotel_id=hotel_data.get('id', f"package-hotel-{package_unique_id}"),
                        offer_id=hotel_data.get('offer_id', f"package-hotel-{package_unique_id}"),
                        check_in=check_in_date,
                        check_out=check_out_date,
                        price=Decimal(hotel_data.get('price_per_night', 0)) * (check_out_date - check_in_date).days,
                        adults=int(adults),
                        room_description=hotel_data.get('description', 'Package Hotel Room')
                    )
                    hotel_cart_item.save()
                    
                    logger.info(f"Added hotel to cart: {hotel_data.get('id')}")
                except Exception as e:
                    logger.error(f"Error adding hotel to cart: {str(e)}")
                    messages.warning(request, f"Could not add hotel to cart: {str(e)}")
            
            # Log activity for the full package
            try:
                activity_title = f"Added package to cart: {package_unique_id}"
                activity_description = f"User {request.user.username} added package {package_unique_id} to cart for ${total_package_price}."
                UserActivity.objects.create(
                    user=request.user,
                    activity_type='add_to_cart',
                    title=activity_title,
                    description=activity_description
                )
            except Exception as e:
                logger.error(f"Error logging add_to_cart activity: {str(e)}")

            messages.success(request, f"Package '{package_unique_id}' added to your cart!")
            return redirect('/cart/')  # Use direct URL path instead of namespace

        except ValueError as ve:
            logger.error(f"ValueError adding package to cart: {str(ve)}")
            messages.error(request, f"Invalid data format for package. Could not add to cart. {str(ve)}")
        except Exception as e:
            logger.error(f"Error adding package to cart: {str(e)}")
            messages.error(request, f"An unexpected error occurred while adding the package to your cart: {str(e)}")
        
        return redirect(request.META.get('HTTP_REFERER', 'trips:home'))  # Fallback redirect
    else:
        # If not POST, redirect to home or results
        messages.info(request, "To add a package to cart, please select one from the search results.")
        return redirect('trips:home')

@login_required
def view_cart(request):
    # Redirect to the main cart view in app1
    return redirect('app1:view_cart')
