from django.db import models
from django.conf import settings

# If you're using a CustomUser model from loginApp
User = settings.AUTH_USER_MODEL


class Hotel(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Additional fields for API compatibility
    hotel_id = models.CharField(max_length=50, unique=True)
    address_line = models.CharField(max_length=255, blank=True)
    city_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=3)
    postal_code = models.CharField(max_length=20, blank=True)
    iata_code = models.CharField(max_length=3, blank=True, null=True)  # 3-letter IATA airport/city code
    rating = models.IntegerField(null=True, blank=True)  # Star rating 1-5
    image_url = models.URLField(max_length=500, blank=True)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    available_rooms = models.IntegerField(default=0)
    # Status (to match the UI)
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('inactive', 'Inactive'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return self.name


class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='rooms')
    room_number = models.CharField(max_length=10)
    room_type = models.CharField(max_length=50, choices=(
        ('standard', 'Standard'),
        ('deluxe', 'Deluxe'),
        ('suite', 'Suite'),
        ('executive', 'Executive'),
        ('family', 'Family')
    ))
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveIntegerField(default=2)
    status = models.CharField(max_length=20, choices=(
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('maintenance', 'Under Maintenance'),
        ('reserved', 'Reserved')
    ), default='available')
    description = models.TextField(blank=True)
    amenities = models.TextField(blank=True, help_text="Comma-separated list of amenities")
    image_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['hotel', 'room_number']
        
    def __str__(self):
        return f"{self.hotel.name} - Room {self.room_number} ({self.room_type})"


class Flight(models.Model):
    airline = models.CharField(max_length=100)
    flight_number = models.CharField(max_length=50)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    # Additional fields for API compatibility
    flight_id = models.CharField(max_length=50, unique=True)
    carrier_code = models.CharField(max_length=10)
    origin_iata = models.CharField(max_length=3)
    destination_iata = models.CharField(max_length=3)
    # Price information
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    taxes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    # Status
    STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('delayed', 'Delayed'),
        ('cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')

    def __str__(self):
        return f"{self.airline} ({self.flight_number})"


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hotel = models.ForeignKey(Hotel, on_delete=models.SET_NULL, null=True, blank=True)
    flight = models.ForeignKey(Flight, on_delete=models.SET_NULL, null=True, blank=True)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)
    check_in = models.DateField(null=True, blank=True)
    check_out = models.DateField(null=True, blank=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=(
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ), default='pending')
    guests = models.PositiveIntegerField(default=1)
    special_requests = models.TextField(blank=True)
    payment_status = models.CharField(max_length=20, choices=(
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
    ), default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Reservation by {self.user} - Status: {self.status}"

    def save(self, *args, **kwargs):
        # Calculate total price if check-in and check-out dates are set
        if self.check_in and self.check_out and self.hotel:
            room_price = self.room.price_per_night if self.room else self.hotel.price_per_night
            days = (self.check_out - self.check_in).days
            self.total_price = room_price * days
        super().save(*args, **kwargs)


class SupportRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=100)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=(
        ('open', 'Open'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ), default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_requests')
    resolution_notes = models.TextField(blank=True)
    priority = models.CharField(max_length=20, choices=(
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ), default='medium')
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.request_type} (Status: {self.status})"
