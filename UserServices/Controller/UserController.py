from rest_framework.views import APIView
from EcommerceInventory.permission import IsSuperAdmin
from EcommerceInventory.Helpers import CommonListAPIMixinWithFilter, executeQuery, renderResponse
from UserServices.models import Modules, UserPermissions, Users
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers

from rest_framework import generics
from EcommerceInventory.Helpers import (
    CustomPageNumberPagination,
    CommonListAPIMixin,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile_pic', 'role']

class UserSerializerWithFilters(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format='%dth %B %Y, %H:%M', read_only=True)
    last_login = serializers.DateTimeField(format='%dth %B %Y, %H:%M', read_only=True)
    domain_user_id=serializers.SerializerMethodField()
    added_by_user_id=serializers.SerializerMethodField()
    class Meta:
        model = Users
        fields = '__all__'
    def get_domain_user_id(self, obj):
        if obj.domain_user_id:
            return (
                "#" + str(obj.domain_user_id.id) + " " + obj.domain_user_id.username
            )
        return ""
    
    def get_added_by_user_id(self, obj):
        if obj.added_by_user_id:
            return (
                "#" + str(obj.added_by_user_id.id) + " " + obj.added_by_user_id.username
            )
        return ""


class UserListView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        users =  Users.objects.filter(domain_user_id=request.user.domain_user_id.id)
        serializer = UserSerializer(users, many=True)
        return renderResponse(data=serializer.data, message="All Users", status=200)
    

class UserWithFiltersListView(generics.ListAPIView):
    serializer_class = UserSerializerWithFilters  
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = Users.objects.all()
        return queryset
    
     #using the mixin to add search and ordering functionality
    @CommonListAPIMixinWithFilter.common_list_decorator(UserSerializerWithFilters)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    

class UpdateUsers(generics.UpdateAPIView):
    serializer_class = UserSerializerWithFilters
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get_queryset(self):
        return Users.objects.filter(
            domain_user_id=self.request.user.domain_user_id.id,
            id=self.kwargs["pk"]
        )

     
    def perform_update(self, serializer):
        serializer.save()


class UserPermissionView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    authentication_classes = [JWTAuthentication]

    def get(self, request, pk):
        query = '''
                SELECT 
                    UserServices_modules.module_name,
                    UserServices_modules.id AS module_id,
                    UserServices_modules.parent_id_id,
                    COALESCE(UserServices_userpermissions.is_permission,0) as is_permission,
                    UserServices_userpermissions.user_id,
                    UserServices_userpermissions.domain_user_id_id 
                    FROM 
                        `UserServices_modules` 
                    LEFT JOIN 
                        UserServices_userpermissions 
                    on 
                        UserServices_userpermissions.module_id=UserServices_modules.id AND
                UserServices_userpermissions.user_id=%s;
                '''
        
        permissions = executeQuery(query, [pk])

        permissionList = {}
        for permission in permissions:
            if permission["parent_id_id"] == None:
                permission["children"] = []
                permissionList[permission["module_id"]] = permission
        
        for permission in permissions:
            if permission["parent_id_id"] != None:
                permissionList[permission["parent_id_id"]]["children"].append(permission)
        
        permissionList = permissionList.values()

        return renderResponse(
            data=permissionList, message="User Permission", status=200
        )
    
    def post(self, request, pk):
        data = request.data 
        for item in data:
            if 'id' in item and item["id"]!=None:
                permission=UserPermissions.objects.get(id=item["id"])
                permission.is_permission=item["is_permission"]
            else:
                module= Modules.objects.get(id=item["module_id"])
                permission=UserPermissions(
                    module=module,
                    user_id=pk,
                    is_permission=item["is_permission"]
                )
            permission.save()
            if "children" in item:
                for child in item["children"]:
                    if 'id' in child and child['id']!=None:
                        permission=UserPermissions.objects.get(id=child["id"])
                        permission.is_permission=child["is_permission"]
                    else:
                        module= Modules.objects.get(id=child["module_id"])

                        permission=UserPermissions(
                        module=module,
                        user_id=pk,
                        is_permission=child["is_permission"]
                    )
                    permission.save()
        return renderResponse(
            data=[],
            message="Permissions Updated",
            status=200
        )
