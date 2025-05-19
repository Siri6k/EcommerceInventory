# middleware.py
import datetime
from UserServices.models import ActivityLog
from django.core.cache import cache
from django.utils import timezone

class UpdateLastLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            # Récupération de l'IP
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip_address:
                ip_address = ip_address.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')

            cache_key = f'visit_limit_{ip_address}'
            if cache.get(cache_key):
                return response
            cache.set(cache_key, True, timeout=10)  # 1 minute timeout
        

            # Récupération de l'appareil (User-Agent)
            user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown Device')

            # Mise à jour des informations dans le modèle User
            request.user.last_login = timezone.now()
            request.user.last_ip = ip_address
            request.user.last_device = user_agent
            request.user.save(update_fields=['last_login', 'last_ip', 'last_device'])

            # Enregistrement de l'activité
            activity_type = "PAGE_VIEW"

            if request.method == "POST":
                activity_type = "FORM_SUBMISSION"
            # Enregistrement dans l'historique
            ActivityLog.objects.create(
                user=request.user,
                activity=f"Accessed {request.path}",
                activity_type=activity_type,
                activity_ip=ip_address,
                activity_device=user_agent
            )

        return response
