from flask import Flask, request, jsonify
import requests
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
DJANGO_BASE_URL = "http://localhost:8000"
HOTEL_SEARCH_ENDPOINT = f"{DJANGO_BASE_URL}/hotels/"
FLIGHT_SEARCH_ENDPOINT = f"{DJANGO_BASE_URL}/flights/search/"

# Helper function to provide sample data based on route
def _get_sample_data(origin_code, destination_code, departure_date, return_date, adults):
    """
    Returns hardcoded sample flight and hotel data for predefined routes.
    """
    flight_options = []
    hotel_options = []

    route_key = f"{origin_code.upper()}-{destination_code.upper()}"

    if route_key == "LHR-JFK":
        flight_options = [
            {
                "id": f"LHR-JFK-FLIGHT-001-{departure_date.replace('-', '')}",
                "carrier": "British Airways (Sample)",
                "price": 550.00 + (adults * 50),
                "departure_datetime": f"{departure_date}T09:00:00",
                "arrival_datetime": f"{departure_date}T12:00:00", # Local JFK
                "return_departure_datetime": f"{return_date}T18:00:00", # Local JFK
                "return_arrival_datetime": f"{return_date}T07:00:00", # Local LHR (next day arrival)
                "origin": "LHR",
                "destination": "JFK",
                "stops": 0,
                "aircraft": "Boeing 777 (Sample)",
                "fare_class": "Economy"
            },
            {
                "id": f"LHR-JFK-FLIGHT-002-{departure_date.replace('-', '')}",
                "carrier": "Virgin Atlantic (Sample)",
                "price": 520.00 + (adults * 45),
                "departure_datetime": f"{departure_date}T11:30:00",
                "arrival_datetime": f"{departure_date}T14:30:00",
                "return_departure_datetime": f"{return_date}T20:00:00",
                "return_arrival_datetime": f"{return_date}T09:00:00",
                "origin": "LHR",
                "destination": "JFK",
                "stops": 1,
                "aircraft": "Airbus A350 (Sample)",
                "fare_class": "Economy"
            }
        ]
        hotel_options = [
            {
                "id": f"JFK-HOTEL-001-{departure_date.replace('-', '')}",
                "name": "The New Yorker (Sample)",
                "price_per_night": 180.00 + (adults * 20),
                "check_in_date": departure_date,
                "check_out_date": return_date,
                "location": "New York, NY",
                "rating": 4.0,
                "amenities": ["WiFi", "Gym", "Restaurant"],
                "room_type": "Standard Queen Room",
                "image_url": "https://via.placeholder.com/300x200.png?text=NYC+Hotel+1"

            },
            {
                "id": f"JFK-HOTEL-002-{departure_date.replace('-', '')}",
                "name": "Times Square Inn (Sample)",
                "price_per_night": 220.00 + (adults * 25),
                "check_in_date": departure_date,
                "check_out_date": return_date,
                "location": "New York, NY",
                "rating": 4.5,
                "amenities": ["WiFi", "Pool", "Bar", "Spa"],
                "room_type": "Deluxe King Room",
                "image_url": "https://via.placeholder.com/300x200.png?text=NYC+Hotel+2"
            }
        ]
    elif route_key == "DEL-BOM":
        flight_options = [
            {
                "id": f"DEL-BOM-FLIGHT-001-{departure_date.replace('-', '')}",
                "carrier": "IndiGo (Sample)",
                "price": 75.00 + (adults * 10),
                "departure_datetime": f"{departure_date}T07:00:00",
                "arrival_datetime": f"{departure_date}T09:00:00",
                "return_departure_datetime": f"{return_date}T19:00:00",
                "return_arrival_datetime": f"{return_date}T21:00:00",
                "origin": "DEL",
                "destination": "BOM",
                "stops": 0,
                "aircraft": "Airbus A320 (Sample)",
                "fare_class": "Economy"
            },
            {
                "id": f"DEL-BOM-FLIGHT-002-{departure_date.replace('-', '')}",
                "carrier": "Air India (Sample)",
                "price": 85.00 + (adults * 12),
                "departure_datetime": f"{departure_date}T10:00:00",
                "arrival_datetime": f"{departure_date}T12:05:00",
                "return_departure_datetime": f"{return_date}T17:00:00",
                "return_arrival_datetime": f"{return_date}T19:05:00",
                "origin": "DEL",
                "destination": "BOM",
                "stops": 0,
                "aircraft": "Boeing 737 (Sample)",
                "fare_class": "Economy"
            }
        ]
        hotel_options = [
            {
                "id": f"BOM-HOTEL-001-{departure_date.replace('-', '')}",
                "name": "The Taj Mahal Palace (Sample View)",
                "price_per_night": 250.00 + (adults * 30),
                "check_in_date": departure_date,
                "check_out_date": return_date,
                "location": "Mumbai",
                "rating": 5.0,
                "amenities": ["Sea View", "Pool", "Fine Dining"],
                "room_type": "Luxury Suite",
                "image_url": "https://via.placeholder.com/300x200.png?text=Mumbai+Hotel+1"
            },
            {
                "id": f"BOM-HOTEL-002-{departure_date.replace('-', '')}",
                "name": "Trident Nariman Point (Sample)",
                "price_per_night": 190.00 + (adults * 20),
                "check_in_date": departure_date,
                "check_out_date": return_date,
                "location": "Mumbai",
                "rating": 4.8,
                "amenities": ["WiFi", "Gym", "Rooftop Bar"],
                "room_type": "Ocean View Room",
                "image_url": "https://via.placeholder.com/300x200.png?text=Mumbai+Hotel+2"
            }
        ]
    elif route_key == "LHR-DEL":
        flight_options = [
            {
                "id": f"LHR-DEL-FLIGHT-001-{departure_date.replace('-', '')}",
                "carrier": "Air India (Sample)",
                "price": 600.00 + (adults * 55),
                "departure_datetime": f"{departure_date}T14:00:00",
                "arrival_datetime": f"{departure_date}T02:30:00", # Next day arrival DEL
                "return_departure_datetime": f"{return_date}T05:00:00", # Local DEL
                "return_arrival_datetime": f"{return_date}T10:00:00", # Local LHR
                "origin": "LHR",
                "destination": "DEL",
                "stops": 0,
                "aircraft": "Boeing 787 (Sample)",
                "fare_class": "Economy"
            }
        ]
        hotel_options = [
            {
                "id": f"DEL-HOTEL-001-{departure_date.replace('-', '')}",
                "name": "The Oberoi (Sample)",
                "price_per_night": 200.00 + (adults * 25),
                "check_in_date": departure_date,
                "check_out_date": return_date,
                "location": "New Delhi",
                "rating": 4.9,
                "amenities": ["Spa", "Pool", "Multiple Restaurants"],
                "room_type": "Premier Room",
                "image_url": "https://via.placeholder.com/300x200.png?text=Delhi+Hotel+1"
            },
            {
                "id": f"DEL-HOTEL-002-{departure_date.replace('-', '')}",
                "name": "Radisson Blu Plaza (Sample)",
                "price_per_night": 120.00 + (adults * 15),
                "check_in_date": departure_date,
                "check_out_date": return_date,
                "location": "New Delhi",
                "rating": 4.3,
                "amenities": ["Airport Shuttle", "Gym", "Restaurant"],
                "room_type": "Business Class Room",
                "image_url": "https://via.placeholder.com/300x200.png?text=Delhi+Hotel+2"
            }
        ]

    return {"flight_options": flight_options, "hotel_options": hotel_options}

# --- Sample Detailed Data Store ---
# We'll use the core part of the ID (without the date) as keys here
SAMPLE_FLIGHT_DETAILS = {
    "LHR-JFK-FLIGHT-001": {
        "id_prefix": "LHR-JFK-FLIGHT-001",
        "carrier": "British Airways (Sample)",
        "origin": "LHR",
        "destination": "JFK",
        "aircraft": "Boeing 777 (Sample)",
        "fare_class": "Economy",
        "departure_terminal": "Terminal 5",
        "arrival_terminal": "Terminal 7",
        "duration_outbound": "8h 00m",
        "duration_return": "7h 30m",
        "baggage_allowance": "1 checked bag (23kg), 1 carry-on",
        "in_flight_services": ["Meals provided", "In-flight entertainment", "WiFi (paid)"],
        "price_breakdown": {
            "base_fare_per_adult": 450.00,
            "taxes_and_fees_per_adult": 100.00,
            "dynamic_adult_surcharge": 50.00 # This was the per-adult addition
        },
        "policy": "Standard economy cancellation and change fees apply. Check with airline."
    },
    "DEL-BOM-FLIGHT-001": {
        "id_prefix": "DEL-BOM-FLIGHT-001",
        "carrier": "IndiGo (Sample)",
        "origin": "DEL",
        "destination": "BOM",
        "aircraft": "Airbus A320 (Sample)",
        "fare_class": "Economy",
        "departure_terminal": "Terminal 1D",
        "arrival_terminal": "Terminal 2",
        "duration_outbound": "2h 00m",
        "duration_return": "2h 00m",
        "baggage_allowance": "15kg checked, 7kg carry-on",
        "in_flight_services": ["Snacks for purchase"],
        "price_breakdown": {
            "base_fare_per_adult": 65.00,
            "taxes_and_fees_per_adult": 10.00,
            "dynamic_adult_surcharge": 10.00
        },
        "policy": "Low-cost carrier, changes and cancellations subject to fees."
    },
    "LHR-DEL-FLIGHT-001": {
        "id_prefix": "LHR-DEL-FLIGHT-001",
        "carrier": "Air India (Sample)",
        "origin": "LHR",
        "destination": "DEL",
        "aircraft": "Boeing 787 (Sample)",
        "fare_class": "Economy",
        "departure_terminal": "Terminal 2",
        "arrival_terminal": "Terminal 3",
        "duration_outbound": "8h 30m",
        "duration_return": "9h 00m",
        "baggage_allowance": "2 checked bags (23kg each), 1 carry-on",
        "in_flight_services": ["Meals provided", "In-flight entertainment"],
        "price_breakdown": {
            "base_fare_per_adult": 500.00,
            "taxes_and_fees_per_adult": 100.00,
            "dynamic_adult_surcharge": 55.00
        },
        "policy": "Check Air India website for latest policies."
    },
    "LHR-JFK-FLIGHT-002": {
        "id_prefix": "LHR-JFK-FLIGHT-002",
        "carrier": "Virgin Atlantic (Sample)",
        "origin": "LHR",
        "destination": "JFK",
        "aircraft": "Airbus A350 (Sample)",
        "fare_class": "Economy",
        "departure_terminal": "Terminal 3",
        "arrival_terminal": "Terminal 4",
        "duration_outbound": "8h 00m (1 stop)",
        "duration_return": "7h 45m (1 stop)",
        "baggage_allowance": "1 checked bag (23kg), 1 carry-on, 1 personal item",
        "in_flight_services": ["Meals provided", "Premium entertainment", "WiFi available"],
        "price_breakdown": {
            "base_fare_per_adult": 420.00,
            "taxes_and_fees_per_adult": 100.00,
            "dynamic_adult_surcharge": 45.00
        },
        "policy": "Flexible economy cancellation and change fees may apply. Confirm with airline."
    },
    "DEL-BOM-FLIGHT-002": {
        "id_prefix": "DEL-BOM-FLIGHT-002",
        "carrier": "Air India (Sample)",
        "origin": "DEL",
        "destination": "BOM",
        "aircraft": "Boeing 737 (Sample)",
        "fare_class": "Economy",
        "departure_terminal": "Terminal 3",
        "arrival_terminal": "Terminal 2",
        "duration_outbound": "2h 05m",
        "duration_return": "2h 05m",
        "baggage_allowance": "20kg checked, 7kg carry-on",
        "in_flight_services": ["Complimentary meal"],
        "price_breakdown": {
            "base_fare_per_adult": 70.00,
            "taxes_and_fees_per_adult": 15.00,
            "dynamic_adult_surcharge": 12.00
        },
        "policy": "Standard Air India domestic policies apply."
    }
}

SAMPLE_HOTEL_DETAILS = {
    "JFK-HOTEL-001": {
        "id_prefix": "JFK-HOTEL-001",
        "name": "The New Yorker (Sample)",
        "location": "New York, NY",
        "rating": 4.0,
        "address": "481 8th Ave, New York, NY 10001, USA",
        "description": "A historic hotel in Midtown Manhattan, offering classic charm and modern amenities. Close to Penn Station and major attractions.",
        "amenities": ["WiFi", "Gym", "Restaurant", "Business Center", "Pet-friendly"],
        "room_types": [
            {"name": "Standard Queen Room", "details": "Comfortable room with one queen bed.", "sample_price_modifier": 0},
            {"name": "Deluxe King Room", "details": "Spacious room with one king bed and city views.", "sample_price_modifier": 50}
        ],
        "images": [
            "https://via.placeholder.com/600x400.png?text=NYC+Hotel+1+View+1",
            "https://via.placeholder.com/600x400.png?text=NYC+Hotel+1+Lobby",
            "https://via.placeholder.com/600x400.png?text=NYC+Hotel+1+Room"
        ],
        "check_in_time": "3:00 PM",
        "check_out_time": "12:00 PM",
        "policies": "Cancellation policies vary. Pets allowed with a fee.",
        "contact": "+1 212-971-0101"
    },
    "BOM-HOTEL-001": {
        "id_prefix": "BOM-HOTEL-001",
        "name": "The Taj Mahal Palace (Sample View)",
        "location": "Mumbai",
        "rating": 5.0,
        "address": "Apollo Bandar, Colaba, Mumbai, Maharashtra 400001, India",
        "description": "Iconic luxury hotel offering breathtaking views of the Gateway of India and the Arabian Sea. Features world-class dining and impeccable service.",
        "amenities": ["Sea View", "Pool", "Fine Dining", "Spa", "Fitness Center", "Butler Service"],
        "room_types": [
            {"name": "Luxury Suite", "details": "Opulent suite with separate living area and stunning views.", "sample_price_modifier": 0},
            {"name": "Maharaja Suite", "details": "The ultimate in luxury, with expansive space and personalized service.", "sample_price_modifier": 500}
        ],
        "images": [
            "https://via.placeholder.com/600x400.png?text=Mumbai+Hotel+1+Exterior",
            "https://via.placeholder.com/600x400.png?text=Mumbai+Hotel+1+Suite",
            "https://via.placeholder.com/600x400.png?text=Mumbai+Hotel+1+Pool"
        ],
        "check_in_time": "2:00 PM",
        "check_out_time": "12:00 PM",
        "policies": "Contact hotel for specific cancellation and deposit policies.",
        "contact": "+91 22-6665-3000"
    },
    "DEL-HOTEL-001": {
        "id_prefix": "DEL-HOTEL-001",
        "name": "The Oberoi (Sample)",
        "location": "New Delhi",
        "rating": 4.9,
        "address": "Dr Zakir Hussain Marg, New Delhi, Delhi 110003, India",
        "description": "A centrally located luxury hotel known for its exceptional service, fine dining, and tranquil ambiance.",
        "amenities": ["Spa", "Pool", "Multiple Restaurants", "24-hour Butler Service", "Air Purification System"],
        "room_types": [
            {"name": "Premier Room", "details": "Elegantly appointed room with city or garden views.", "sample_price_modifier": 0},
            {"name": "Luxury Suite", "details": "Spacious suite with a separate living room and personalized amenities.", "sample_price_modifier": 200}
        ],
        "images": [
            "https://via.placeholder.com/600x400.png?text=Delhi+Hotel+1+Facade",
            "https://via.placeholder.com/600x400.png?text=Delhi+Hotel+1+Room+View",
            "https://via.placeholder.com/600x400.png?text=Delhi+Hotel+1+Restaurant"
        ],
        "check_in_time": "2:00 PM",
        "check_out_time": "12:00 PM",
        "policies": "Standard cancellation policies apply. Contact hotel for details.",
        "contact": "+91 11-2436-3030"
    },
    "JFK-HOTEL-002": {
        "id_prefix": "JFK-HOTEL-002",
        "name": "Times Square Inn (Sample)",
        "location": "New York, NY",
        "rating": 4.5,
        "address": "790 7th Ave, New York, NY 10019, USA",
        "description": "Modern hotel located steps from Times Square, offering comfortable rooms and convenient access to theaters and shopping.",
        "amenities": ["WiFi", "Pool", "Bar", "Spa", "Concierge", "Fitness Center"],
        "room_types": [
            {"name": "Deluxe King Room", "details": "Well-appointed room with a king-size bed.", "sample_price_modifier": 0},
            {"name": "City View Suite", "details": "Suite with separate living area and views of Times Square.", "sample_price_modifier": 100}
        ],
        "images": [
            "https://via.placeholder.com/600x400.png?text=NYC+Hotel+2+Exterior",
            "https://via.placeholder.com/600x400.png?text=NYC+Hotel+2+Room",
            "https://via.placeholder.com/600x400.png?text=NYC+Hotel+2+Pool"
        ],
        "check_in_time": "4:00 PM",
        "check_out_time": "11:00 AM",
        "policies": "Prepayment and cancellation policies vary by rate. Check specific booking conditions.",
        "contact": "+1 212-555-0202"
    },
    "BOM-HOTEL-002": {
        "id_prefix": "BOM-HOTEL-002",
        "name": "Trident Nariman Point (Sample)",
        "location": "Mumbai",
        "rating": 4.8,
        "address": "Netaji Subhash Chandra Bose Road, Nariman Point, Mumbai, Maharashtra 400021, India",
        "description": "Elegant hotel offering panoramic views of the Arabian Sea, renowned for its excellent service and dining options.",
        "amenities": ["WiFi", "Gym", "Rooftop Bar", "Outdoor Pool", "Business Centre", "Multiple Restaurants"],
        "room_types": [
            {"name": "Ocean View Room", "details": "Comfortable room with stunning views of the ocean.", "sample_price_modifier": 0},
            {"name": "Club Level Room", "details": "Access to Club Lounge with additional benefits.", "sample_price_modifier": 75}
        ],
        "images": [
            "https://via.placeholder.com/600x400.png?text=Mumbai+Hotel+2+Lobby",
            "https://via.placeholder.com/600x400.png?text=Mumbai+Hotel+2+View",
            "https://via.placeholder.com/600x400.png?text=Mumbai+Hotel+2+Restaurant"
        ],
        "check_in_time": "2:00 PM",
        "check_out_time": "12:00 PM",
        "policies": "Cancellation policy depends on the rate booked. Refer to booking confirmation.",
        "contact": "+91 22-6632-4343"
    },
    "DEL-HOTEL-002": {
        "id_prefix": "DEL-HOTEL-002",
        "name": "Radisson Blu Plaza (Sample)",
        "location": "New Delhi",
        "rating": 4.3,
        "address": "National Highway 8, New Delhi, Delhi 110037, India",
        "description": "Conveniently located near the airport, this hotel offers modern rooms, a spa, and multiple dining options.",
        "amenities": ["Airport Shuttle", "Gym", "Restaurant", "Outdoor Pool", "Spa", "Free WiFi"],
        "room_types": [
            {"name": "Business Class Room", "details": "Spacious room with enhanced amenities for business travelers.", "sample_price_modifier": 0},
            {"name": "Superior Room", "details": "Comfortable and well-equipped room.", "sample_price_modifier": -20}
        ],
        "images": [
            "https://via.placeholder.com/600x400.png?text=Delhi+Hotel+2+Exterior",
            "https://via.placeholder.com/600x400.png?text=Delhi+Hotel+2+Pool",
            "https://via.placeholder.com/600x400.png?text=Delhi+Hotel+2+Room"
        ],
        "check_in_time": "3:00 PM",
        "check_out_time": "12:00 PM",
        "policies": "Flexible cancellation available for most rates. Check specific conditions.",
        "contact": "+91 11-2677-9191"
    }
}

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint to verify the API is working"""
    return jsonify({
        "status": "ok",
        "message": "Trip Planner API is running"
    })

@app.route("/api/trip/search", methods=["POST"])
def search_trip():
    """
    Endpoint to search for trip options (hotels + flights)
    
    Expects JSON data with:
    - destination: city name or airport code
    - origin: origin city name or airport code (for flights)
    - departure_date: YYYY-MM-DD format
    - return_date: YYYY-MM-DD format
    - adults: number of adults
    """
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Extract and validate required parameters
    destination = data.get('destination')
    origin = data.get('origin')
    departure_date = data.get('departure_date')
    return_date = data.get('return_date')
    adults = data.get('adults', 1)
    
    if not (destination and origin and departure_date and return_date):
        return jsonify({
            "error": "Missing required parameters. Please provide destination, origin, departure_date, and return_date."
        }), 400

    # Check for predefined sample routes first
    sample_data = _get_sample_data(origin, destination, departure_date, return_date, adults)

    # Debug print for LHR-JFK route
    if origin.upper() == "LHR" and destination.upper() in ["JFK", "NYC"]:
        try:
            print(f"DEBUG LHR-JFK sample_data: {json.dumps(sample_data, indent=2)}")
        except Exception as e:
            print(f"Error printing LHR-JFK sample_data: {e}")

    if sample_data["flight_options"] or sample_data["hotel_options"]:
        # Use sample data if available for the route
        flights_data = {"success": True, "flight_options": sample_data["flight_options"]}
        hotels_data = {"success": True, "hotel_options": sample_data["hotel_options"]}
    else:
        # Fallback to original (basic placeholder) search if no specific sample data
        # Note: These original functions also return very basic placeholders
        flights_data = search_flights(origin, destination, departure_date, return_date, adults)
        hotels_data = search_hotels(destination, departure_date, return_date, adults)

    # Combine and process results
    trip_options = process_trip_options(hotels_data, flights_data)
    
    return jsonify({
        "trip_options": trip_options,
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "adults": adults
    })

def search_flights(origin, destination, departure_date, return_date, adults):
    """
    Call the Django flight search endpoint (or return basic placeholders).
    This function now primarily serves as a fallback if no specific sample data is found.
    """
    try:
        params = {
            'origin': origin,
            'destination': destination,
            'departure_date': departure_date,
            'return_date': return_date,
            'adults': adults,
            'trip_type': 'round'
        }
        
        response = requests.get(FLIGHT_SEARCH_ENDPOINT, params=params, timeout=60)
        
        if response.status_code == 200:
            # Since the Django endpoint returns HTML, we'll need to
            # extract the flight data or create a dedicated API endpoint
            # For simplicity, we'll just return some sample data for now
            # This is a VERY basic placeholder
            return {
                "success": True,
                "flight_options": [
                    {
                        "id": f"fallback-flight-{departure_date.replace('-', '')}",
                        "carrier": "Fallback Airline",
                        "price": 299.99 + (adults * 20),
                        "departure_datetime": f"{departure_date}T12:00:00",
                        "arrival_datetime": f"{departure_date}T15:00:00",
                        "return_departure_datetime": f"{return_date}T12:00:00",
                        "return_arrival_datetime": f"{return_date}T15:00:00",
                        "origin": origin,
                        "destination": destination,
                        "stops": 0,
                        "aircraft": "Generic Jet",
                        "fare_class": "Economy"
                    }
                ]
            }
        else:
            return {"success": False, "error": f"Error calling flight API: {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def search_hotels(destination, check_in, check_out, adults):
    """
    Call the Django hotel search endpoint (or return basic placeholders).
    This function now primarily serves as a fallback if no specific sample data is found.
    """
    try:
        params = {
            'city': destination,
            'check_in': check_in,
            'check_out': check_out,
            'adults': adults
        }
        
        response = requests.get(HOTEL_SEARCH_ENDPOINT, params=params, timeout=60)
        
        if response.status_code == 200:
            # Since the Django endpoint returns HTML, we'll need to
            # extract the hotel data or create a dedicated API endpoint
            # For simplicity, we'll just return some sample data for now
            # This is a VERY basic placeholder
            return {
                "success": True,
                "hotel_options": [
                    {
                        "id": f"fallback-hotel-{check_in.replace('-', '')}",
                        "name": "Fallback Sample Hotel",
                        "price_per_night": 129.99 + (adults * 10),
                        "check_in_date": check_in,
                        "check_out_date": check_out,
                        "location": destination,
                        "rating": 3.5,
                        "amenities": ["WiFi"],
                        "room_type": "Standard Room",
                        "image_url": "https://via.placeholder.com/300x200.png?text=Fallback+Hotel"
                    }
                ]
            }
        else:
            return {"success": False, "error": f"Error calling hotel API: {response.status_code}"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def process_trip_options(hotels_data, flights_data):
    """Process and combine hotel and flight data to create trip options"""
    if not (hotels_data.get('success', False) and flights_data.get('success', False)):
        # If either flight or hotel search failed, or returned no options, return empty
        # This check is a bit lenient; robust error handling might be needed
        # if not hotels_data.get('hotel_options') and not flights_data.get('flight_options'):
        #     return [] # Only return empty if BOTH are empty
        pass # Allow processing even if one part is missing, to show partial results

    hotel_options = hotels_data.get('hotel_options', [])
    flight_options = flights_data.get('flight_options', [])

    # Create combined trip options
    trip_options = []

    # If no flights or no hotels, we might still want to show what we have,
    # or create packages if at least one of each exists.
    # For now, let's create packages only if we have both.
    # A more advanced version could create flight-only or hotel-only packages too.

    if not flight_options and not hotel_options:
        return [] # No options to combine

    # Scenario 1: We have flights and hotels
    if flight_options and hotel_options:
        for hotel in hotel_options[:3]:  # Limit to first 3 hotels
            for flight in flight_options[:2]:  # Limit to first 2 flights
                # Simple duration calculation (difference between check_out and check_in)
                # This requires date objects for accurate calculation.
                # For simplicity with string dates, let's assume a fixed number of nights or derive from hotel.
                # If hotel object contains number_of_nights, use it. Otherwise, a fallback.
                num_nights = 3 # Default
                try:
                    from datetime import datetime
                    check_in_dt = datetime.strptime(hotel['check_in_date'], '%Y-%m-%d')
                    check_out_dt = datetime.strptime(hotel['check_out_date'], '%Y-%m-%d')
                    num_nights = (check_out_dt - check_in_dt).days
                    if num_nights <= 0: num_nights = 1 # Ensure at least 1 night
                except (ValueError, KeyError):
                    pass # Keep default if dates are not parsable or not present

                trip_option = {
                    "id": f"trip-{flight['id']}-{hotel['id']}",
                    "flight": flight,
                    "hotel": hotel,
                    "total_price": round(flight['price'] + (hotel['price_per_night'] * num_nights), 2),
                    "savings": round((flight['price'] * 0.05) + (hotel['price_per_night'] * num_nights * 0.03), 2) # Sample savings
                }
                trip_options.append(trip_option)
    # Scenario 2: Only flights available
    elif flight_options:
        for flight in flight_options[:2]:
             trip_options.append({
                "id": f"trip-flightonly-{flight['id']}",
                "flight": flight,
                "hotel": None, # No hotel
                "total_price": round(flight['price'], 2),
                "savings": round(flight['price'] * 0.05, 2)
            })
    # Scenario 3: Only hotels available
    elif hotel_options:
        for hotel in hotel_options[:3]:
            num_nights = 3 # Default
            try:
                from datetime import datetime
                check_in_dt = datetime.strptime(hotel['check_in_date'], '%Y-%m-%d')
                check_out_dt = datetime.strptime(hotel['check_out_date'], '%Y-%m-%d')
                num_nights = (check_out_dt - check_in_dt).days
                if num_nights <= 0: num_nights = 1
            except (ValueError, KeyError):
                pass

            trip_options.append({
                "id": f"trip-hotelonly-{hotel['id']}",
                "flight": None, # No flight
                "hotel": hotel,
                "total_price": round(hotel['price_per_night'] * num_nights, 2),
                "savings": round(hotel['price_per_night'] * num_nights * 0.03, 2)
            })

    return trip_options

@app.route("/api/flight/details/<path:flight_id>", methods=["GET"])
def get_flight_details(flight_id):
    # Extract the core part of the flight ID (e.g., "LHR-JFK-FLIGHT-001")
    # The ID format from search is like "LHR-JFK-FLIGHT-001-YYYYMMDD"
    # We want to match against the ID prefix.
    
    # A simple way to get the prefix (everything before the last dash, if it contains date)
    # Or, more robustly, split by '-' and rejoin the relevant parts.
    # Assuming flight IDs from search are like ROUTE-TYPE-NUMBER-DATESTRING
    id_parts = flight_id.split('-')
    if len(id_parts) > 3 and id_parts[-1].isdigit() and len(id_parts[-1]) == 8: # Check for date part
        core_id = "-".join(id_parts[:-1])
    else:
        core_id = flight_id # Assume it might be a core ID already, or different format

    if core_id in SAMPLE_FLIGHT_DETAILS:
        details = SAMPLE_FLIGHT_DETAILS[core_id].copy() # Return a copy
        # Potentially, you could use the date part from flight_id if needed for dynamic details
        details['full_id_requested'] = flight_id # Add the full ID for reference
        return jsonify(details)
    else:
        # Fallback for flight IDs not in our detailed sample store (e.g., "fallback-flight-...")
        if flight_id.startswith("fallback-flight-"):
            return jsonify({
                "id_prefix": flight_id,
                "carrier": "Fallback Airline",
                "origin": "N/A",
                "destination": "N/A",
                "aircraft": "Generic Jet",
                "fare_class": "Economy",
                "departure_terminal": "TBD",
                "arrival_terminal": "TBD",
                "duration_outbound": "N/A",
                "duration_return": "N/A",
                "baggage_allowance": "Basic",
                "in_flight_services": ["Basic service"],
                "price_breakdown": {"base_fare_per_adult": 200.00, "taxes_and_fees_per_adult": 50.00, "dynamic_adult_surcharge": 20.00},
                "policy": "Standard fallback policy.",
                "full_id_requested": flight_id,
                "message": "This is fallback detailed information."
            })
        return jsonify({"error": "Flight details not found"}), 404

@app.route("/api/hotel/details/<path:hotel_id>", methods=["GET"])
def get_hotel_details(hotel_id):
    # Similar logic for hotel_id as for flight_id
    id_parts = hotel_id.split('-')
    if len(id_parts) > 3 and id_parts[-1].isdigit() and len(id_parts[-1]) == 8: # Check for date part
        core_id = "-".join(id_parts[:-1])
    else:
        core_id = hotel_id

    if core_id in SAMPLE_HOTEL_DETAILS:
        details = SAMPLE_HOTEL_DETAILS[core_id].copy()
        details['full_id_requested'] = hotel_id
        # You could add date-specific info here if needed, e.g., dynamic pricing based on date from hotel_id
        return jsonify(details)
    else:
        # Fallback for hotel IDs not in our detailed sample store (e.g., "fallback-hotel-...")
        if hotel_id.startswith("fallback-hotel-"):
            return jsonify({
                "id_prefix": hotel_id,
                "name": "Fallback Sample Hotel",
                "location": "Unknown",
                "rating": 3.0,
                "address": "N/A",
                "description": "This is basic fallback hotel information.",
                "amenities": ["Basic amenities"],
                "room_types": [{"name": "Standard Fallback Room", "details": "Basic room.", "sample_price_modifier": 0}],
                "images": ["https://via.placeholder.com/600x400.png?text=Fallback+Hotel+Detail"],
                "check_in_time": "N/A",
                "check_out_time": "N/A",
                "policies": "Standard fallback policy.",
                "contact": "N/A",
                "full_id_requested": hotel_id,
                "message": "This is fallback detailed information."
            })
        return jsonify({"error": "Hotel details not found"}), 404

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000) 