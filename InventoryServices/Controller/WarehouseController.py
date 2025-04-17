from tkinter import W
from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


from InventoryServices.models import RackAndShelvesAndFloor, Warehouse
from EcommerceInventory.Helpers import CommonListAPIMixin, CustomPageNumberPagination


class RackShelfFloorSerializer(serializers.ModelSerializer):
    domain_user_id= serializers.SerializerMethodField()
    added_by_user_id= serializers.SerializerMethodField()
    warehouse_id= serializers.SerializerMethodField()
    class Meta:
        model = RackAndShelvesAndFloor
        fields = '__all__'
    
    def get_domain_user_id(self, obj):
        return "#"+str(obj.domain_user_id.id)+" "+obj.domain_user_id.username
    
    def get_added_by_user_id(self, obj):
        return "#"+str(obj.added_by_user_id.id)+" "+obj.added_by_user_id.username
    def get_warehouse_id(self, obj):
        return "#"+str(obj.warehouse_id.id)+" "+obj.warehouse_id.name

class WarehouseSerializer(serializers.ModelSerializer):
    domain_user_id= serializers.SerializerMethodField()
    added_by_user_id= serializers.SerializerMethodField()
    warehouse_manager= serializers.SerializerMethodField()
    rack_shelf_floor= serializers.SerializerMethodField()
    class Meta:
        model = Warehouse
        fields = '__all__'

    def get_domain_user_id(self, obj):
        return "#"+str(obj.domain_user_id.id)+" "+obj.domain_user_id.username
    
    def get_added_by_user_id(self, obj):
        return "#"+str(obj.added_by_user_id.id)+" "+obj.added_by_user_id.username
    def get_warehouse_manager(self, obj):
        return "#"+str(obj.warehouse_manager.id)+" "+obj.warehouse_manager.username
    
    def get_rack_shelf_floor(self, obj):
        rack_shelf_floor = RackAndShelvesAndFloor.objects.filter(warehouse_id=obj.id)
        serializer = RackShelfFloorSerializer(rack_shelf_floor, many=True)
        return serializer.data

class WarehouseListView(generics.ListAPIView):
    serializer_class = WarehouseSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = Warehouse.objects.filter(
            domain_user_id=self.request.user.domain_user_id.id
        )
        return queryset
    
     #using the mixin to add search and ordering functionality
    @CommonListAPIMixin.common_list_decorator(WarehouseSerializer)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
  
class UpdateWarehouseView(generics.UpdateAPIView):
    serializer_class = WarehouseSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Warehouse.objects.filter(
            domain_user_id=self.request.user.domain_user_id.id,
            id=self.kwargs["pk"]
        )

     
    def perform_update(self, serializer):
        serializer.save()
