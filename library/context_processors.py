from django.utils import timezone


def site_settings(request):
    return {
        'SITE_NAME': 'My Library',
        'YEAR': timezone.now().year,
    }