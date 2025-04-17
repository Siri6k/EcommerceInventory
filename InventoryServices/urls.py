from django.urls import path

from .Controller.WarehouseController import UpdateWarehouseView, WarehouseListView

urlpatterns = [
    path('warehouse/', WarehouseListView.as_view(), name='warehouse_list'),
    path('toggleWarehouse/<int:pk>/', UpdateWarehouseView.as_view(), name='update_warehouse'),
]
