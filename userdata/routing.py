from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('fulldata/ws/procces/', consumers.Proccess.as_asgi()),
]