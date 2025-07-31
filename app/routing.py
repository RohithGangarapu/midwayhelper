# routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/track/(?P<ride_id>[^/]+)/$', consumers.RideTrackingConsumer.as_asgi()),
]
