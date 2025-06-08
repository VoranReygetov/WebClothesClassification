from django.urls import re_path
from detection import streaming


websocket_urlpatterns = [
    re_path(r'ws/stream/$', streaming.VideoStreamConsumer.as_asgi()),
]