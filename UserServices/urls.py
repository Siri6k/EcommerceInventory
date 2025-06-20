from django.urls import path, include
from UserServices.Controller import ProfileController
from UserServices.Controller import AuthController, UserController, SocialController
from UserServices.views import MyTokenRefreshView, MyTokenObtainPairView

urlpatterns = [

    path('social/google/', SocialController.GoogleLoginAPIView.as_view(), name='google_login'), 


    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),

    path("login/", AuthController.LoginAPIView.as_view(), name="login"),
    path("signup/", AuthController.SignupAPIView.as_view(), name="login"),
    path("publicApi/", AuthController.PublicAPIView.as_view(), name="public"),
    path("protectedApi/", AuthController.ProtectedAPIView.as_view(), name="protected"),
    path("superadminurl/", AuthController.SuperAdminCheckApi.as_view(), name="superadmin"),
    path("users/", UserController.UserListView.as_view(), name="user_list"),
    path("userList/", UserController.UserWithFiltersListView.as_view(), name="user_list_filter"),
    path("updateUser/<pk>/", UserController.UpdateUsers.as_view(), name="user_update"),
    path("userpermission/<pk>/", UserController.UserPermissionView.as_view(), name="user_permission"),
    path("getMyProfile/", ProfileController.UserProfileView.as_view(), name="my_profile"),
    path("getProfile/<pk>/", ProfileController.ProfileView.as_view(), name="users_profile"),
    path("updateMyProfile/", ProfileController.UpdateUserFormController.as_view(), name="update_user_profile"),
]
