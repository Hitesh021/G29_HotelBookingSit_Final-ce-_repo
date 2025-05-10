from django.urls import path
from . import views

app_name = 'trips'  # This defines the namespace

urlpatterns = [
    path('', views.trip_planner_home, name='home'),
    path('search/', views.trip_planner_search, name='search'),
    path('results/', views.trip_planner_results, name='results'),
    path('details/<str:trip_id>/', views.trip_details, name='details'),
    path('flight-details/<path:flight_id>/', views.flight_item_details_view, name='flight_item_details'),
    path('hotel-details/<path:hotel_id>/', views.hotel_item_details_view, name='hotel_item_details'),
    path('add-to-cart/', views.add_package_to_cart, name='add_package_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
] 