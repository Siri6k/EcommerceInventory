from rest_framework_simplejwt.views import TokenObtainPairView
from UserServices.serializers import MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenRefreshView
from UserServices.serializers import MyTokenRefreshSerializer


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class MyTokenRefreshView(TokenRefreshView):
    serializer_class = MyTokenRefreshSerializer