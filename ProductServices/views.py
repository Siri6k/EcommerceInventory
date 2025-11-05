from django.shortcuts import render

# Create your views here.
from django_filters import rest_framework as filters
from .models import Products

class ProductFilter(filters.FilterSet):
    price_min = filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_max = filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Products
        fields = ["price_min", "price_max", "category"]
