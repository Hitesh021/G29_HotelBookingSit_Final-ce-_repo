from django.db import models
from django.conf import settings # To get the User model
from django.utils import timezone

class TripPackageCartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trip_package_cart_items')
    
    # Overall Package Info
    package_unique_id = models.CharField(max_length=255, help_text="A unique ID for the package, e.g., trip-flightid-hotelid")
    total_package_price = models.DecimalField(max_digits=10, decimal_places=2)
    adults = models.PositiveIntegerField(default=1)
    # Store original search dates for reference or re-calculation if needed
    search_departure_date = models.DateField()
    search_return_date = models.DateField()

    # Flight Details Snapshot
    flight_id = models.CharField(max_length=255, blank=True, null=True)
    flight_carrier = models.CharField(max_length=255, blank=True, null=True)
    flight_origin = models.CharField(max_length=100, blank=True, null=True)
    flight_destination = models.CharField(max_length=100, blank=True, null=True)
    flight_departure_datetime = models.CharField(max_length=50, blank=True, null=True) # Storing as char from API
    flight_return_datetime = models.CharField(max_length=50, blank=True, null=True)    # Storing as char from API
    flight_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Hotel Details Snapshot
    hotel_id = models.CharField(max_length=255, blank=True, null=True)
    hotel_name = models.CharField(max_length=255, blank=True, null=True)
    hotel_location = models.CharField(max_length=255, blank=True, null=True)
    hotel_check_in_date = models.CharField(max_length=20, blank=True, null=True) # Storing as char from API
    hotel_check_out_date = models.CharField(max_length=20, blank=True, null=True)# Storing as char from API
    hotel_price_per_night = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    num_nights = models.PositiveIntegerField(blank=True, null=True)

    # Raw JSON data (optional, but can be useful)
    # Ensure your database supports JSONField (PostgreSQL, MySQL 5.7.8+, SQLite 3.38.0+ with JSON1 extension)
    # For broader compatibility, you could use TextField and store JSON as a string.
    flight_details_json = models.JSONField(blank=True, null=True)
    hotel_details_json = models.JSONField(blank=True, null=True)

    added_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Package for {self.user.username} - {self.package_unique_id} (${self.total_package_price})"

    class Meta:
        ordering = ['-added_on']
        verbose_name = "Trip Package Cart Item"
        verbose_name_plural = "Trip Package Cart Items"
