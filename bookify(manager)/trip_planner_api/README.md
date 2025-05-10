# Trip Planner API

This Flask API serves as the orchestration layer for the Trip Planner feature, combining hotel and flight data from the main Django application.

## Features

- Fetches hotel and flight data from existing Django endpoints
- Combines and processes results to create trip packages
- Provides RESTful API endpoints for the Django frontend to consume

## Setup

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the API:
   ```
   python app.py
   ```

The API will be available at `http://localhost:5000`.

## API Endpoints

### Health Check
- **GET /api/health**
  - Returns a simple status message to verify the API is running

### Trip Search
- **POST /api/trip/search**
  - Accepts JSON payload with search parameters
  - Returns combined hotel and flight options
  - Parameters:
    - `destination`: City name or airport code (string, required)
    - `origin`: Origin city name or airport code (string, required)
    - `departure_date`: Departure date in YYYY-MM-DD format (string, required)
    - `return_date`: Return date in YYYY-MM-DD format (string, required)
    - `adults`: Number of adults (integer, default: 1)

## Integration with Django

This API is designed to work with the main Django application, calling its existing hotel and flight search endpoints and providing a unified response.

## Running in Production

For production deployment, use Gunicorn:
```
gunicorn app:app -b 0.0.0.0:5000
``` 