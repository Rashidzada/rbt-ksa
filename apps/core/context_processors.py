from types import SimpleNamespace
from django.conf import settings
from .models import SiteSetting

def site_settings(request):
    settings_obj = SiteSetting.objects.first()
    if settings_obj:
        return {'site_settings': settings_obj}

    return {
        'site_settings': SimpleNamespace(
            support_whatsapp_number=settings.SUPPORT_WHATSAPP_NUMBER
        )
    }
