from django.urls import path

from OrderServices.Controller.PurchaseOrderController import CreatePurchaseOrderView, PurchaseOrderListView


urlpatterns = [
    path("purchaseOrder/", CreatePurchaseOrderView.as_view(), name='purchase_order'),
    path("purchaseOrder/<str:id>/", CreatePurchaseOrderView.as_view(), name='purchase_order_draft_details'),
    path("purchaseOrderList/", PurchaseOrderListView.as_view(), name='purchase_order_list'),

]
