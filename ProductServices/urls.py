from django.urls import path

from .controller.ProductController import (
    ProductAllListView,
    ProductListView,
    ProductReviewListView,
    CreateProductReviewView,
    UpdateProductReviewView,
    ProductQuestionsListView,
    CreateProductQuestionView,
    UpdateProductQuestionView,
)
from .controller.CategoryController import CategoryListView


urlpatterns = [
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("", ProductListView.as_view(), name="product-list"),
    path("all/", ProductAllListView.as_view(), name="all-product-list"),
   ## Product Review API list, create, update
    path("productReviews/<str:product_id>/", ProductReviewListView.as_view(), name="product-review-list"),
    path("createProductReview/<str:product_id>/", CreateProductReviewView.as_view(), name="create-product-review"),
    path("updateProductReview/<str:product_id>/<pk>/", UpdateProductReviewView.as_view(), name="update-product-review"),
    ## Product Question API list, create, update
    path("productQuestions/<str:product_id>/", ProductQuestionsListView.as_view(), name="product-question-list"),
    path("createProductQuestion/<str:product_id>/", CreateProductQuestionView.as_view(), name="create-product-question"),
    path("updateProductQuestion/<str:product_id>/<pk>/", UpdateProductQuestionView.as_view(), name="update-product-question"),
      
]
