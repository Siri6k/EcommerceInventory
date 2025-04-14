from unicodedata import category
from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Q
from django.db import models

from EcommerceInventory.Helpers import (
    CommonListAPIMixin, CustomPageNumberPagination, renderResponse
)
from ProductServices.models import Products

class ProductSerializer(serializers.ModelSerializer):
    category_id= serializers.SerializerMethodField()
    domain_user_id= serializers.SerializerMethodField()
    added_by_user_id= serializers.SerializerMethodField()

    class Meta:
        model = Products
        fields = '__all__'

    def get_category_id(self, obj):
        return "#"+str(obj.category_id.id)+" "+obj.category_id.name
    
    def get_domain_user_id(self, obj):
        return "#"+str(obj.domain_user_id.id)+" "+obj.domain_user_id.username
    
    def get_added_by_user_id(self, obj):
        return "#"+str(obj.added_by_user_id.id)+" "+obj.added_by_user_id.username
   
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination
    
    def get_queryset(self):
        queryset = Products.objects.filter(
            domain_user_id=self.request.user.domain_user_id.id
        )
        return queryset
    
     #using the mixin to add search and ordering functionality
    @CommonListAPIMixin.common_list_decorator(ProductSerializer)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
 
