from django.http import JsonResponse
from UserServices.models import ModuleUrls, UserPermissions
from rest_framework_simplejwt.authentication import JWTAuthentication
import re
from django.db.models import Q


class PermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        current_url = request.path

        # Skip URLs that don't require authentication
        if current_url in urlToSkip():
            return response
        
        # Try JWT authentication
        jwt_auth = JWTAuthentication()
        
        try:
            auth_result = jwt_auth.authenticate(request)
            if auth_result is None:
                # Check if this is a public endpoint that should be allowed
                if is_public_endpoint(current_url):
                    return response
                return JsonResponse({"message":"Unauthorized - Invalid token"}, status=401)
                
            user, token = auth_result
        except Exception as e:
            # Log the error for debugging
            return JsonResponse({"message":"Unauthorized - Authentication failed"}, status=401)
        
        # Skip permission logic for super admin and top level user
        if user.role == "Super Admin" or (hasattr(user, 'domain_user_id') and user.domain_user_id.id == user.id):
            return response
        
        module = find_matching_module(current_url)
        if not module:
            # Consider whether missing module should be 404 or 403
            return JsonResponse({"message":"Resource Not Found"}, status=404)
        
        permission = UserPermissions.objects.filter(user=user.id, module=module.module).first()
        
        if not permission or permission.is_permission == False:
            return JsonResponse({"message":"Permission Denied"}, status=403)
        
        return response

def is_public_endpoint(url):
    # Add logic to identify public endpoints (like login, health checks, etc.)
    public_urls = ['/api/auth/login/', '/health/', '/','/auth/','']  # Add your public URLs here
    return url in public_urls

def urlToSkip():
    modules = ModuleUrls.objects.filter(module__isnull=True).values_list('url', flat=True)
    return modules

def find_matching_module(url):
    regex_pattern = re.sub(r'\d+','[^\/]+', url.replace('/','\/'))

    match_patter  = ModuleUrls.objects.filter(Q(url__iregex=f'^{regex_pattern}$')).first()

    return match_patter