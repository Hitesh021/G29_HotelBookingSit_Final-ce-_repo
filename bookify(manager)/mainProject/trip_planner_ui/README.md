# Trip Planner UI

This Django app provides the user interface for the Trip Planner feature, which combines hotel and flight booking options into a single, unified experience.

## Features

- Search form for trip planning (origin, destination, dates, travelers)
- Results page displaying combined flight + hotel packages
- Detailed trip view with comprehensive information
- Integration with the Flask Trip Planner API

## How It Works

1. Users enter search criteria in the trip planner search form
2. The Django app sends this data to the Flask API
3. The Flask API orchestrates calls to the existing hotel and flight services
4. Results are combined and returned to the Django app
5. The Django app renders the results in a user-friendly interface

## Templates

- `trip_planner_home.html` - Search form
- `trip_planner_results.html` - List of trip options
- `trip_details.html` - Detailed view of a specific trip

## Views

- `trip_planner_home` - Renders the search form
- `trip_planner_search` - Processes form submission
- `trip_planner_results` - Displays search results
- `trip_details` - Shows detailed information for a specific trip

## URLs

- `/trips/` - Home/search page
- `/trips/search/` - Form submission endpoint
- `/trips/results/` - Search results
- `/trips/details/<trip_id>/` - Trip details

## Integration

This app communicates with the Flask Trip Planner API, which in turn communicates with the existing Django hotel and flight services. 