from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


from UserServices.models import Users
from EcommerceInventory.Helpers import (
    CommonListAPIMixin, CustomPageNumberPagination, renderResponse
)
from ProductServices.models import ProductQuestions, ProductReviews, Products

class ProductReviewSerializer(serializers.ModelSerializer):
    review_user_id= serializers.SerializerMethodField()
    domain_user_id= serializers.SerializerMethodField()
    class Meta:
        model = ProductReviews
        fields = '__all__'
    
    def get_review_user_id(self, obj):
        return "#"+str(obj.review_user_id.id)+" "+obj.review_user_id.username
    
    def get_domain_user_id(self, obj):
        return "#"+str(obj.domain_user_id.id)+" "+obj.domain_user_id.username

class ProductQuestionSerializer(serializers.ModelSerializer):
    domain_user_id= serializers.SerializerMethodField()
    question_user_id= serializers.SerializerMethodField()
    answer_user_id= serializers.SerializerMethodField()
    class Meta:
        model = ProductQuestions
        fields = '__all__'

    def get_domain_user_id(self, obj):
        return "#"+str(obj.domain_user_id.id)+" "+obj.domain_user_id.username
    def get_question_user_id(self, obj):
        return "#"+str(obj.question_user_id.id)+" "+obj.question_user_id.username
    def get_answer_user_id(self, obj):
        return "#"+str(obj.answer_user_id.id)+" "+obj.answer_user_id.username

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
        user = obj.added_by_user_id
        if not user:
            return None
        
        return {
            "id": user.id,
            "username": user.username,
            "whatsapp_number": user.whatsapp_number,
            "country": user.country,
            "city": user.city

        }

class ProductListSerializer(serializers.ModelSerializer):
    category_id= serializers.SerializerMethodField()
    added_by_user_id= serializers.SerializerMethodField()
    class Meta:
        model = Products
        fields = ["id", "name", 
                  "category_id", "image", 
                  "description",
                  "added_by_user_id",
                  "price", "quantity",
                  "updated_at"]
        
    def get_category_id(self, obj):
        return "#"+str(obj.category_id.id)+" "+obj.category_id.name
        
    def get_added_by_user_id(self, obj):
        user = obj.added_by_user_id
        if not user:
            return None
        
        return {
            "id": user.id,
            "username": user.username,
            "whatsapp_number": user.whatsapp_number,
            "country": user.country,
            "city": user.city

        }

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = Products.objects.filter(
            added_by_user_id=self.request.user.added_by_user_id.id
        )
        return queryset
    
     #using the mixin to add search and ordering functionality
    @CommonListAPIMixin.common_list_decorator(ProductSerializer)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    

 
############### Review and questions API #######################

class ProductReviewListView(generics.ListAPIView):
    serializer_class = ProductReviewSerializer  
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = ProductReviews.objects.filter(
            domain_user_id=self.request.user.domain_user_id.id,
            product_id=self.kwargs['product_id']
        )
        return queryset
    
     #using the mixin to add search and ordering functionality
    @CommonListAPIMixin.common_list_decorator(ProductReviewSerializer)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    

class ProductQuestionsListView(generics.ListAPIView):
    serializer_class = ProductQuestionSerializer  
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = ProductQuestions.objects.filter(
            domain_user_id=self.request.user.domain_user_id.id,
            product_id=self.kwargs['product_id']
        )
        return queryset
    
     #using the mixin to add search and ordering functionality
    @CommonListAPIMixin.common_list_decorator(ProductQuestionSerializer)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
class CreateProductReviewView(generics.CreateAPIView):
    serializer_class = ProductReviewSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.data.get("review_user_id"):
            serializer.save(
                domain_user_id=self.request.user.domain_user_id,
                review_user_id=Users.objects.get(
                    id=int(self.request.data.get("review_user_id"))
                    ),
                product_id=Products.objects.get(id=self.kwargs["product_id"])
            )
        else:
            serializer.save(
                domain_user_id=self.request.user.domain_user_id,
                product_id=Products.objects.get(id=self.kwargs["product_id"]),
                review_user_id=self.request.user
            )


class CreateProductQuestionView(generics.CreateAPIView):
    serializer_class = ProductQuestionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.data.get("question_user_id") and self.request.data.get("answer_user_id"):
            serializer.save(
                domain_user_id=self.request.user.domain_user_id,
                question_user_id=Users.objects.get(id=int(self.request.data.get("question_user_id"))),
                answer_user_id=Users.objects.get(
                    id=int(self.request.data.get("answer_user_id"))
                ),
                product_id=Products.objects.get(id=self.kwargs["product_id"])

            )
        else:
            serializer.save(
                domain_user_id=self.request.user.domain_user_id,
                product_id=Products.objects.get(id=self.kwargs["product_id"]),
                question_user_id=self.request.user,
                answer_user_id=self.request.user
            )   

    
class UpdateProductReviewView(generics.UpdateAPIView):
    serializer_class = ProductReviewSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProductReviews.objects.filter(
            domain_user_id=self.request.user.domain_user_id.id,
            product_id=Products.objects.get(id=self.kwargs["product_id"]),
            id=self.kwargs["pk"]
        )

     
    def perform_update(self, serializer):
        serializer.save()

class UpdateProductQuestionView(generics.UpdateAPIView):
    serializer_class = ProductQuestionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProductQuestions.objects.filter(
            domain_user_id=self.request.user.domain_user_id.id,
            product_id=Products.objects.get(id=self.kwargs["product_id"]),
            id=self.kwargs["pk"]
        )
     
    def perform_update(self, serializer):
        if self.request.data.get("answer"):
            if self.request.data.get("answer_user_id"):
                serializer.save(
                    answer_user_id=Users.objects.get(
                        id=int(self.request.data.get("answer_user_id")))
                )
            else:
                serializer.save(                  
                    answer_user_id=self.request.user
                )
        else:
            serializer.save()
    


class ProductAllListView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = Products.objects.all()
        return queryset
    
     #using the mixin to add search and ordering functionality
    @CommonListAPIMixin.common_list_decorator(ProductListSerializer)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    


class ProductDetailView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Products.objects.filter(
            id=self.kwargs["pk"]
        )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        product = serializer.data
        # Fetching reviews and questions related to the product
        reviews = ProductReviews.objects.filter(
                        product_id=instance.id
                    )
        
        if not reviews.exists():
            reviews = []
        else:
            reviews = ProductReviewSerializer(reviews, many=True).data

        questions = ProductQuestions.objects.filter(
                        product_id=instance.id
                    )
        if not questions.exists():
            questions = []
        else:
            questions = ProductQuestionSerializer(questions, many=True).data
        
        return renderResponse(
            data={
                "product": product,
                "reviews": reviews,
                "questions": questions
            },
            message="Product details retrieved successfully.",
            status=200
        )