from django.contrib import admin
from .models import TripPackageCartItem

@admin.register(TripPackageCartItem)
class TripPackageCartItemAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'package_unique_id',
        'flight_carrier',
        'hotel_name',
        'total_package_price',
        'adults',
        'added_on'
    )
    list_filter = ('user', 'added_on', 'flight_carrier', 'hotel_name')
    search_fields = (
        'user__username',
        'package_unique_id',
        'flight_id',
        'hotel_id',
        'flight_carrier',
        'hotel_name'
    )
    readonly_fields = ('added_on',)
    fieldsets = (
        (None, {
            'fields': ('user', 'package_unique_id', 'total_package_price', 'adults')
        }),
        ('Search Parameters', {
            'fields': ('search_departure_date', 'search_return_date')
        }),
        ('Flight Info', {
            'classes': ('collapse',),
            'fields': (
                'flight_id', 'flight_carrier', 'flight_origin', 'flight_destination',
                'flight_departure_datetime', 'flight_return_datetime', 'flight_price',
                'flight_details_json'
            )
        }),
        ('Hotel Info', {
            'classes': ('collapse',),
            'fields': (
                'hotel_id', 'hotel_name', 'hotel_location', 'hotel_check_in_date',
                'hotel_check_out_date', 'hotel_price_per_night', 'num_nights',
                'hotel_details_json'
            )
        }),
        ('Timestamps', {
            'fields': ('added_on',)
        })
    )
