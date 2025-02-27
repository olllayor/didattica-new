# config/routing.py
from django.urls import re_path
from accounts import consumers

websocket_urlpatterns = [
    re_path(r"ws/presence/$", consumers.PresenceConsumer.as_asgi()),
]