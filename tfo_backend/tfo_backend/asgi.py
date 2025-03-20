"""
ASGI config for tfo_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""


import os

import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE","tfo_backend.settings")

print("DJANGO_SETTINGS_MODULE:", os.environ.get('DJANGO_SETTINGS_MODULE'))
django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from organizations.routing import websocket_urlpatterns  


print("Initializing ASGI application...")
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
