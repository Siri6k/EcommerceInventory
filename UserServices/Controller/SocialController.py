from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.utils import timezone
from rest_framework.views import APIView
import uuid
from django.utils.crypto import get_random_string
import os
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from UserServices.models import Users, Modules, UserPermissions

DEFAULT_PROFILE_PIC = [
    "https://res.cloudinary.com/dihwey5iz/image/upload/v1749648449/uploads/jgqz3fxfaqjay0slxi5a.png"
]

class GoogleLoginAPIView(APIView):
    def post(self, request):
        token = request.data.get('access_token')
        if not token:
            return Response({"error": "Missing access_token"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Vérification du token Google
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                os.getenv("GOOGLE_CLIENT_ID")
            )
            
            email = idinfo.get("email")
            if not email:
                return Response({"error": "Email not provided by Google"}, status=status.HTTP_400_BAD_REQUEST)
                
            # Tentative de récupération de l'utilisateur existant
            try:
                user = Users.objects.get(email=email)
                created = False
                
                # Mise à jour des informations SAUF le username
                user.first_name = idinfo.get("given_name", user.first_name)
                user.last_name = idinfo.get("family_name", user.last_name)
                user.social_provider = "google"
                user.social_uid = idinfo["sub"]
                user.social_extra_data = idinfo
                
                user.save()
                
            except Users.DoesNotExist:
                # Création d'un nouvel utilisateur
                username = email.split('@')[0]
                google_pic = idinfo.get("picture")
                profile_pic = (
                    {"url": google_pic} if google_pic 
                    else DEFAULT_PROFILE_PIC
                )
                
                user = Users.objects.create(
                    email=email,
                    username=username,
                    first_name=idinfo.get("given_name", ""),
                    last_name=idinfo.get("family_name", ""),
                    profile_pic=profile_pic,
                    anon_id=str(uuid.uuid4()),
                    social_provider="google",
                    social_uid=idinfo["sub"],
                    social_extra_data=idinfo,
                )
                
                # Mot de passe aléatoire sécurisé
                user.set_password(get_random_string(12))
                user.save()
                created = True

                # Attribution des permissions par défaut
                default_modules = [45, 46, 18, 19, 28, 27]
                for module_id in default_modules:
                    try:
                        module = Modules.objects.get(id=module_id)
                        UserPermissions.objects.create(
                            module=module,
                            user_id=user.id,
                            is_permission=1
                        )
                    except Modules.DoesNotExist:
                        continue

            # Génération du token JWT
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            # Ajout des claims personnalisés
            access["username"] = user.username
            access["email"] = user.email
            access["profile_pic"] = user.profile_pic if user.profile_pic else ""
            access["role"] = user.role
            access["phone_number"] = user.phone_number if user.phone_number else ""
            access["address"] = user.address if user.address else ""
            access["anon_id"] = user.anon_id if user.anon_id else ""

            # Journalisation des informations de connexion
            ip = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown Device')
            
            user.last_ip = ip
            user.last_device = user_agent[:255]  # Troncature si nécessaire
            user.last_login = timezone.now()
            user.save(update_fields=['last_ip', 'last_device', 'last_login'])

            return Response({
                "refresh": str(refresh),
                "access": str(access),
                "message": "Google login successful",
                "is_new_user": created
            }, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": "Invalid Google token", "details": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"error": "Authentication failed", "details": str(e)}, status=status.HTTP_400_BAD_REQUEST)