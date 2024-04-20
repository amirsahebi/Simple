from django.urls import path

import fulldetail.consumers
import data.consumers
from . import consumers

websocket_urlpatterns = [
    path('ws/procces', consumers.Proccess.as_asgi()),
    path('fulldata/ws/procces', fulldetail.consumers.Proccess.as_asgi()),
    path('getuser/ws/procces', data.consumers.Proccess.as_asgi()),
]