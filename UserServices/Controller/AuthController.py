from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication  # type: ignore
from django.contrib.auth import authenticate
from UserServices.models import Modules, UserPermissions, Users
from EcommerceInventory.Helpers import renderResponse
from EcommerceInventory.permission import IsSuperAdmin
from django.utils import timezone



from rest_framework_simplejwt.tokens import RefreshToken


from allauth.socialaccount.models import SocialAccount

class SignupAPIView(APIView):
    def post(self, request):
        username = request.data.get("username")
        email = request.data.get("email")
        password = request.data.get("password")
        profile_pic = request.data.get("profile_pic")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        phone_number = request.data.get("phone_number")
        whatsapp_number = request.data.get("whatsapp_number")
        address = request.data.get("address")
        province = request.data.get("province")
        city = request.data.get("city")
        anon_id = request.data.get("anon_id")

        emailcheck = Users.objects.filter(email=email)
        if emailcheck.exists():
            return renderResponse(data="Email Already Exists", message="Email Already Exists", status=status.HTTP_400_BAD_REQUEST)

        usernamecheck = Users.objects.filter(username=username)
        if usernamecheck.exists():
            return renderResponse(data="Username Already Exists", message="Username Already Exists", status=status.HTTP_400_BAD_REQUEST)

        if username is None or password is None or email is None:
            return renderResponse(data="Please provide both username and password", message="Please provide both username and password", status=status.HTTP_400_BAD_REQUEST)
        
        

        user = Users.objects.create_user(
            username=username,
            email=email,
            password=password,
            profile_pic=profile_pic,
            address=address,
            phone_number=phone_number,
            whatsapp_number=whatsapp_number,
            first_name=first_name,
            last_name=last_name,
            province=province,
            city=city,
            anon_id=anon_id,
        )

        if request.data.get("domain_user_id"):
            user.domain_user_id = Users.objects.get(
                id=request.data.get("domain_user_id"))
            
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            ip_address = ip_address.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        # Récupération de l'appareil (User-Agent)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown Device')
            # Mise à jour des informations dans le modèle User

        user.last_login = timezone.now()
        user.last_ip = ip_address
        user.last_device = user_agent
        user.save()
      
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        access["username"] = user.username
        access["email"] = user.email
        access["profile_pic"] = user.profile_pic if user.profile_pic else ""
        access["role"] = user.role
        access["phone_number"] = user.phone_number if user.phone_number else ""
        access["address"] = user.address if user.address else ""
        access["anon_id"] = user.anon_id if user.anon_id else ""


         #Save default permissions (dashboard, analytics and settings)
        default_modules = [45,46,18,19,28,27]
        user_id = Users.objects.filter(email=email).values("id")

        for module_id in default_modules:
            module= Modules.objects.get(id=module_id)
            permission=UserPermissions(
                    module=module,
                    user_id=user_id,
                    is_permission=1
                )
            permission.save()

        return Response(
            {
                "refresh": str(refresh),
                "access": str(access),
                "message": "User Created Successfully!",
            },
            status=status.HTTP_201_CREATED,
        )


class LoginAPIView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if username is None or password is None:
            return renderResponse(data="Please provide both username and password", message="Please provide both username and password", status=status.HTTP_400_BAD_REQUEST)
        
       

        user = authenticate(request, username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            access["username"] = user.username
            access["email"] = user.email
            access["profile_pic"] = user.profile_pic if user.profile_pic else ""
            access["role"] = user.role
            access["phone_number"] = user.phone_number if user.phone_number else ""
            access["address"] = user.address if user.address else ""
            access["anon_id"] = user.anon_id if user.anon_id else ""



            ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
            if ip_address:
                ip_address = ip_address.split(',')[0]
            else:
                ip_address = request.META.get('REMOTE_ADDR')

            # Récupération de l'appareil (User-Agent)
            user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown Device')
             # Mise à jour des informations dans le modèle User

            user.last_login = timezone.now()
            user.last_ip = ip_address
            user.last_device = user_agent
            user.save(update_fields=['last_login', 'last_ip', 'last_device'])

            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(access),
                }
            )
        else:
            return renderResponse(
                data="Invalid username or password",
                message="Invalid username or password",
                status=status.HTTP_400_BAD_REQUEST
            )

    def get(self, request):
        return renderResponse(
            data="Please Use Post to Login!",
            message="Please Use Post to Login!",
            status=status.HTTP_400_BAD_REQUEST
        )


class PublicAPIView(APIView):
    def get(self, request):
        return renderResponse(
            data="This is a public API!",
            message="This is a public API!",
            status=status.HTTP_400_BAD_REQUEST
        )


class ProtectedAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return renderResponse(
            data="This is a protected API!",
            message="This is a protected API!",
            status=status.HTTP_400_BAD_REQUEST
        )
    
class SuperAdminCheckApi(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        return renderResponse(
            data="This is a Super Admin API!",
            message="This is a Super Admin API!",
            status=status.HTTP_400_BAD_REQUEST
        )


