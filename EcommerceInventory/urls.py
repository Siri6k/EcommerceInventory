# Removed unused 'index' import from operator
from django.contrib import admin
from django.urls import path, include, re_path

from UserServices.Controller.SidebarController import (
    ModuleView, ModuleUrlsListAPIView
)
from UserServices.Controller.ModuleController import (
    SuperAdminDynamicFormController,
)
from UserServices.Controller.DynamicFormController import DynamicFormController

from EcommerceInventory import settings
from django.conf.urls.static import static

from EcommerceInventory.views import FileUploadViewInS3, index

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("UserServices.urls")),
    path(
        "api/getForm/<str:modelName>/",
        DynamicFormController.as_view(),
        name="dynamicForm",
    ),
    path(
        "api/getForm/<str:modelName>/<str:id>/",
        DynamicFormController.as_view(),
        name="dynamicForm",
    ),
    path(
        "api/superAdminForm/<str:modelName>/",
        SuperAdminDynamicFormController.as_view(),
        name="SuperAdmindynamicForm",
    ),
    path(
        "api/moduleUrls/",
        ModuleUrlsListAPIView.as_view(),
        name="moduleUrls_superadmin",
    ),
    path(
        "api/getMenus/",
        ModuleView.as_view(),
        name="sidebarmenu",
    ),
    path("api/products/", include("ProductServices.urls")),
    path("api/inventory/", include("InventoryServices.urls")),
    
    path(
        "api/orders/", include("OrderServices.urls")),
    path(
        "api/uploads/",
        FileUploadViewInS3.as_view(),
        name="fileupload",
    ),
]

if settings.DEBUG:
    urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns+=[
    re_path(r'^(?:.*)/?$', index, name='index')
]