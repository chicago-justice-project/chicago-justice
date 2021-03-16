from django.conf import settings
from django.http import HttpRequest

def google_analytics(request: HttpRequest):
    return {
        'GA_KEY': settings.GOOGLE_ANALYTICS_KEY,
    }
