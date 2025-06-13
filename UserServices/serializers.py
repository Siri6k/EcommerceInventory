from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework import serializers
# your_app/serializers.py
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Claims personnalisés
        token["username"] = user.username
        token["role"] = user.role
        token["email"] = user.email
        token["phone_number"] = user.phone_number or ""
        token["profile_pic"] = user.profile_pic.url if user.profile_pic else ""
        token["whatsapp_number"] = user.whatsapp_number or ""
        token["address"] = user.address or ""
        token["anon_id"] = user.anon_id or ""

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        return data
    
class MyTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        try:
            refresh = RefreshToken(attrs["refresh"])
            user_id = refresh["user_id"]
            user = User.objects.get(id=user_id)
        except (KeyError, User.DoesNotExist, TokenError):
            raise InvalidToken("Invalid token or user does not exist")
        
        # Génère un nouveau token d'accès avec les custom claims
        access = AccessToken.for_user(user)
        access["username"] = user.username
        access["role"] = user.role
        access["email"] = user.email
        access["phone_number"] = user.phone_number or ""
        access["profile_pic"] = user.profile_pic if user.profile_pic else ""
        access["whatsapp_number"] = user.whatsapp_number or ""
        access["address"] = user.address or ""
        access["anon_id"] = user.anon_id or ""

        # Remplace le token access par le tien
        data["access"] = str(access)       
    

        return data

