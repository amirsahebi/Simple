from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('getuser/ws/procces1', consumers.Proccess.as_asgi()),
    
]