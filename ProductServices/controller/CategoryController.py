from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q
from django.db import models
from rest_framework.views import APIView


from EcommerceInventory.Helpers import (
    CommonListAPIMixin, CustomPageNumberPagination, renderResponse
)
from ProductServices.models import Categories

class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    domain_user_id= serializers.SerializerMethodField()
    added_by_user_id= serializers.SerializerMethodField()
    class Meta:
        model = Categories
        fields = '__all__'

    def get_children(self, obj):
        children = Categories.objects.filter(parent_id=obj.id)
        return CategorySerializer(children, many=True).data
    
    def get_domain_user_id(self, obj):
        return "#"+str(obj.domain_user_id.id)+" "+obj.domain_user_id.username
    
    def get_added_by_user_id(self, obj):
        return "#"+str(obj.added_by_user_id.id)+" "+obj.added_by_user_id.username
   
    
class CategoryListView(generics.ListAPIView):
    serializer_class = CategorySerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = Categories.objects.filter(parent_id__isnull=True).filter(
            domain_user_id=self.request.user.domain_user_id.id
        )
        
        return queryset
    
    #using the mixin to add search and ordering functionality
    @CommonListAPIMixin.common_list_decorator(CategorySerializer)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
 
class AllCategorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Categories
        fields = ["id", "name"]

   

class AllCategoryListView(APIView):

    def get(self, request):
        categories = Categories.objects.all()
        serializer = AllCategorySerializer(categories, many=True)
        return renderResponse(data=serializer.data, message="All list Categories", status=200)

