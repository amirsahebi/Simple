# mysite/asgi.py
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application1 = get_asgi_application()


# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.

import tokenmanager.routing
import core.urls

application = ProtocolTypeRouter({
  "http": application1,
  "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                tokenmanager.routing.websocket_urlpatterns
            )
        )
    ),
})

