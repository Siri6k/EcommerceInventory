from django.urls import path

from OrderServices.Controller.PurchaseOrderController import CreatePurchaseOrderView


urlpatterns = [
    path("purchaseOrder/", CreatePurchaseOrderView.as_view(), name='purchase_order'),
]
