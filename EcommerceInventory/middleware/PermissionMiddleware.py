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

        # Check dynamic patterns like <pk> or <id>
        for public_url in self.public_urls:
            # Convert <pk>, <id> or <slug> style to regex
            pattern = re.sub(r'<[^>]+>', '[^/]+', public_url)
            pattern = pattern.rstrip('/') + '/?$'  # match with or without trailing slash
            if re.fullmatch(pattern, normalized_url):
                return True

        return False

        
    
    
    def find_matching_module(self, url):
        """Find module with URL pattern matching"""
        # Convert numeric IDs to pattern
        pattern = re.sub(r'/\d+/', '/[^/]+/', url)
        pattern = re.sub(r'/\d+$', '/[^/]+', pattern)
        
        # Escape special regex chars except our patterns
        pattern = re.escape(pattern)
        pattern = pattern.replace('\\[^\\/\\]\\+', '[^/]+')
        
        return ModuleUrls.objects.filter(
            Q(url__iregex=f'^{pattern}$') |
            Q(url__iregex=f'^{pattern}/$')
        ).first()
    
    def _has_permission(self, user, module):
        """Check if user has permission for the module"""
        permission = UserPermissions.objects.filter(
            user=user.id,
            module=module.module
        ).first()
        return permission and permission.is_permission
