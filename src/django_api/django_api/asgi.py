"""
ASGI config for django_api project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/

This configuration supports both HTTP and WebSocket protocols via Django Channels.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_api.settings")

# Initialize Django ASGI application early to populate AppRegistry
# before importing consumers and routing
django_asgi_app = get_asgi_application()


def get_application():
    """
    Build and return the ASGI application with WebSocket support.

    Uses Django Channels for WebSocket routing when available,
    falls back to standard Django ASGI otherwise.
    """
    try:
        from channels.auth import AuthMiddlewareStack
        from channels.routing import ProtocolTypeRouter, URLRouter
        from channels.security.websocket import AllowedHostsOriginValidator
        from pdf_service.routing import websocket_urlpatterns

        return ProtocolTypeRouter(
            {
                "http": django_asgi_app,
                "websocket": AllowedHostsOriginValidator(
                    AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
                ),
            }
        )
    except ImportError:
        # Channels not installed, return standard Django application
        return django_asgi_app


application = get_application()
