from django.http import JsonResponse
from UserServices.models import ModuleUrls, UserPermissions
from rest_framework_simplejwt.authentication import JWTAuthentication
import re
from django.db.models import Q
from urllib.parse import urlparse


class PermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.public_urls = self._load_public_urls()
    
    def _load_public_urls(self):
        """Preload public URLs from database and hardcoded ones"""
        db_public_urls = list(ModuleUrls.objects.filter(module__isnull=True).values_list('url', flat=True))
        hardcoded_public_urls = [
            '/api/auth/login/',
            '/api/auth/signup/',
            '/health/',
            '/',
            '/auth/',
            '/api/auth/refresh/',
            '/api/docs/',
            ''
        ]
        return set(db_public_urls + hardcoded_public_urls)
    
    def __call__(self, request):
        response = self.get_response(request)
        current_url = request.path
        
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
        return user.role == "Super Admin" or (hasattr(user, 'domain_user_id') and user.domain_user_id.id == user.id)
    
    def is_public_endpoint(self, url):
        """Improved public endpoint detection"""
        # Normalize URL for comparison
        normalized_url = url.rstrip('/') + '/'
        
        # Check exact matches
        if normalized_url in self.public_urls:
            return True
            
        # Check pattern matches (for URLs with IDs, etc.)
        for public_url in self.public_urls:
            if public_url.endswith('*'):
                if url.startswith(public_url[:-1]):
                    return True
            elif public_url.endswith('/+'):
                base_url = public_url[:-2]
                if url.startswith(base_url):
                    return True
        
        # Special cases (could be moved to config)
        public_path_segments = {'manage', 'form', 'create', 'home', 'static', 'media'}
        if any(segment in url.lower() for segment in public_path_segments):
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
