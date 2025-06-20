from django.http import JsonResponse
from UserServices.models import ModuleUrls, UserPermissions
from rest_framework_simplejwt.authentication import JWTAuthentication
import re
from django.db.models import Q
from urllib.parse import urlparse
from django.conf import settings


class PermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.public_urls = self._load_public_urls()
    
    def _load_public_urls(self):
        """Preload public URLs from database and hardcoded ones"""
        db_public_urls = list(ModuleUrls.objects.filter(module__isnull=True).values_list('url', flat=True))
        print(db_public_urls)
        hardcoded_public_urls = [
            '/api/auth/login/',
            '/api/auth/signup/',
            '/health/',
            '/',
            '/auth/',
            '/api/auth/refresh/',
            '/api/docs/',
            '',
            '/api/products/all/',
            '/api/products/detail/*/',
            '/api/save-visit/',
            '/api/uploads/',
            '/api/auth/social/google/'
            'api/auth/social/google/callback/',
            '/api/auth/social/google/login/',
            '/api/auth/social/google/logout/',
            '/api/auth/social/google/complete/',
            '/api/auth/social/google/authorize/',
            '/api/auth/social/google/authorized/',
            "api/auth/registration/",
            '/api/auth/registration/account-confirm-email/',
            '/api/auth/registration/account-confirm-email/*/',
            '/api/auth/registration/account-confirm-email/*/confirm/',
            '/api/auth/registration/account-confirm-email/*/resend/',
            '/api/auth/registration/account-confirm-email/*/verify/',
            '/api/auth/registration/account-confirm-email/*/verify-email/',
            '/api/auth/google/login/',
            '/api/auth/google/signup/',
            '/api/auth/google/callback/',
            '/api/auth/google/login/',
            '/api/auth/google/logout/',
            '/api/auth/google/complete/',
            '/api/auth/google/authorize/',
            '/api/auth/google/authorized/',
            '/api/auth/google/authorize/',
            '/api/auth/google/authorized/',
            "/api/auth/google/signup/",
            "/api/auth/social/google/",
        ]
        return set(db_public_urls + hardcoded_public_urls)
    
    def __call__(self, request):
        self._load_public_urls()  # Ensure public URLs are loaded
        # Process the request
        response = self.get_response(request)
        current_url = request.path

        # Autoriser automatiquement tous les liens frontend (hors API)
        if not current_url.startswith('/api/') and not settings.DEBUG:
            return self.get_response(request)
        
        # Skip public URLs
        if self.is_public_endpoint(current_url):
            return response
        
        # Try JWT authentication
        try:
            auth_result = JWTAuthentication().authenticate(request)
            if auth_result is None:
                return JsonResponse({"message": "Unauthorized - Invalid token"}, status=401)
                
            user, token = auth_result
        except Exception as e:
            return JsonResponse({"message": "Unauthorized - Authentication failed"}, status=401)
        
        # Bypass permission checks for super users
        if self._is_super_user(user):
            return response
        
        # Check permissions
        module = self.find_matching_module(current_url)
        if not module:
            return JsonResponse({"message": "Resource Not Found"}, status=404)
        
        if not self._has_permission(user, module):
            return JsonResponse({"message": "Permission Denied"}, status=403)
        
        return response
    
    def _is_super_user(self, user):
        """Check if user has super admin privileges"""
       
        return user.role == "Super Admin" or (
            hasattr(user, 'domain_user_id') 
            and user.domain_user_id is not None 
            and user.domain_user_id.id == user.id)
    
    def is_public_endpoint(self, url):
        """Check if the URL matches a known public URL pattern"""
        normalized_url = url.rstrip('/') + '/'

        # Check exact match
        if normalized_url in self.public_urls:
            return True

        for public_url in self.public_urls:
            pattern = public_url.rstrip('/') + '/'
            pattern = pattern.replace('.', r'\.')  # Escape dots

            # Replace Django-like path converters with regex
            pattern = re.sub(r'<int:[^>]+>', r'\\d+', pattern)  # Note double backslash
            pattern = re.sub(r'<str:[^>]+>', r'[^/]+', pattern)
            pattern = re.sub(r'<slug:[^>]+>', r'[-a-zA-Z0-9_]+', pattern)
            pattern = re.sub(r'<[^>]+>', r'[^/]+', pattern)  # fallback: <pk>, <id>, etc.

            pattern += '/?'  # optional trailing slash

            if re.fullmatch(pattern, normalized_url):
                return True

        return False 
    
    def find_matching_module(self, url):
        """
        Match incoming URL with patterns stored in the database, like:
        /api/getForm/<str:modelName>/<str:id>/
        /api/products/detail/<pk>/
        """

        # Normalize trailing slash
        if not url.endswith("/"):
            url += "/"

        # List of Django-style path converters and their regex equivalents
        # Note: Using double backslashes for regex patterns
        placeholder_patterns = {
            r"<int:[^>/]+>": r"\\d+",  # Double backslash
            r"<str:[^>/]+>": r"[^/]+",
            r"<slug:[^>/]+>": r"[-a-zA-Z0-9_]+",
            r"<uuid:[^>/]+>": r"[0-9a-fA-F-]+",
            r"<[^>/]+>": r"[^/]+",  # fallback for <pk>, <id>, etc.
        }

        # Fetch all candidate patterns from DB
        all_patterns = ModuleUrls.objects.all()

        for pattern_obj in all_patterns:
            pattern = pattern_obj.url

            # Add trailing slash for consistency
            if not pattern.endswith("/"):
                pattern += "/"

            # Escape regex special characters in the pattern
            escaped_pattern = re.escape(pattern)

            # Replace escaped placeholders with regex
            for placeholder, regex in placeholder_patterns.items():
                escaped_placeholder = re.escape(placeholder)
                # Use raw string for the replacement
                escaped_pattern = re.sub(escaped_placeholder, regex.replace('\\', r'\\'), escaped_pattern)

            # Compile and test the regex
            if re.fullmatch(escaped_pattern, url):
                return pattern_obj

        return None

    
    def _has_permission(self, user, module):
        """Check if user has permission for the module"""
        permission = UserPermissions.objects.filter(
            user=user.id,
            module=module.module
        ).first()
        return permission and permission.is_permission