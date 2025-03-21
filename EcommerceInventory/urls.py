# Removed unused 'index' import from operator
from django.contrib import admin
from django.urls import path, include, re_path

from UserServices.Controller.SidebarController import (
    ModuleView,
)
from UserServices.Controller.ModuleController import (
    SuperAdminDynamicFormController,
)
from UserServices.Controller.DynamicFormController import DynamicFormController

from EcommerceInventory import settings
from django.conf.urls.static import static

from views import index

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("UserServices.urls")),
    path(
        "api/getForm/<str:modelName>/",
        DynamicFormController.as_view(),
        name="dynamicForm",
    ),
    path(
        "api/superAdminForm/<str:modelName>/",
        SuperAdminDynamicFormController.as_view(),
        name="SuperAdmindynamicForm",
    ),
    path(
        "api/getMenus/",
        ModuleView.as_view(),
        name="sidebarmenu",
    ),
    path("api/products/", include("ProductServices.urls")),
]

if settings.DEBUG:
    urlpatterns+=static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns+=[
    re_path(r'^(?:.*)/?$', index, name='index')
]