from django.urls import path
from .views import *

urlpatterns = [
    path('register/',register,name='register_user'),
    path('',login,name='login'),
    path('home/',home,name="home"),
    path('createride/',createride,name="createride"),
    path('searchride/',search_ride,name="searchride"),
    path('ride_details/<str:id>/',ride_details,name="ride_details"),
    path('book/<str:driver>/',book,name="book"),
    path('bookings/',booking_list,name="bookings"),
    path('driver/',driver,name="driver"),
    path('ride_ticket/<str:id>/',ticket,name="ticket"),
    path('tracking/<str:id>/',tracking,name="track"),
    # User endpoints
    path('users/', UserViewSet.as_view({'get':'list','post': 'create'}), name='create_user'),
    
    # Journey endpoints
    path('journeys/', JourneyViewSet.as_view({'post': 'create', 'get': 'list'}), name='journey_list_create'),
    
    # Search journeys
    path('journeys/search/', JourneySearchView.as_view(), name='journey_search'),
]
