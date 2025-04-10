from django.urls import path

from .controller.ProductController import ProductListView
from .controller.CategoryController import CategoryListView


urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("", ProductListView.as_view(), name="product-list"),

    
]
