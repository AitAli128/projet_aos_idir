from django.conf import settings


def public_endpoints(request):
    return {
        "PUBLIC_AUTH_URL": settings.PUBLIC_AUTH_URL,
        "PUBLIC_API_URL": settings.PUBLIC_API_URL,
    }
