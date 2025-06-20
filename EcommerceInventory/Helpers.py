import json
from django.db.models import ForeignKey

from django.urls import URLPattern
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
)
from rest_framework.pagination import PageNumberPagination

from django.forms.models import model_to_dict
from functools import wraps
from django.db import connection, models
from django.db.models import Q

from datetime import date, datetime
from django.utils import timezone
from django.urls.resolvers import (URLPattern, get_resolver, URLResolver)
from django.core.serializers import serialize



def getDynamicFormModels():
    return {
        "product": "ProductServices.Products",
        "category": "ProductServices.Categories",
        "warehouse": "InventoryServices.Warehouse",
        "supplier": "UserServices.Users",
        "rackShelfFloor": "InventoryServices.RackAndShelvesAndFloor",
        "users": "UserServices.Users",


    }


def getSuperAdminDynamicFormModels():
    return {
        "modules": "UserServices.Modules",
    }


def checkIsFiledFields(field):
    return field in ["image", "file", "path", "video", "audio", "profile_pic"]


def getExcludeFields():
    return [
        "id",
        "created_at",
        "updated_at",
        "domain_user_id",
        "added_by_user_id",
        "created_by_user_id",
        "updated_by_user_id",
        "domain_name",
        "last_login",
        "last_device",
        "last_ip",
        "is_active",
        "is_superuser",
        "is_staff",
        "date_joined",
        "sku",
    ]
def getDynamicFormFields(model_instance, domain_user_id, skip_related=[],skip_fields=[]):
    fields = {
        "text": [],
        "select": [],
        "checkbox": [],
        "radio": [],
        "textarea": [],
        "json": [],
        "file": [],
    }
    for field in model_instance._meta.fields:
        if field.name in getExcludeFields() or field.name in skip_fields:
            continue

        label = field.name.replace("_", " ").title()
        fielddata = {
            "name": field.name,
            "label": label,
            "placeholder": "Enter " + label,
            "default": (
                model_instance.__dict__[field.name]
                if field.name in model_instance.__dict__
                else ""
            ),
            "required": not field.null,
        }

      
        if checkIsFiledFields(field.name):
            fielddata["type"] = "file"
        elif field.get_internal_type() == "TextField":
            fielddata["type"] = "textarea"
        elif field.get_internal_type() == "JSONField":
            fielddata["type"] = "json"
        elif field.get_internal_type() == "CharField" and field.choices:
            fielddata["type"] = "select"
            fielddata["options"] = [
                {"id": choice[0], "value": choice[1]} for choice in field.choices
            ]

        elif (
            field.get_internal_type() == 'CharField' or
            field.get_internal_type() == 'IntegerField' or
            field.get_internal_type() == 'DecimalField' or
            field.get_internal_type() == 'FloatField'
        ):
            fielddata['type'] = 'text'
        elif (
            field.get_internal_type() == "BooleanField"
            or field.get_internal_type() == "NullBooleanField"
        ):
            fielddata["type"] = "checkbox"
        elif field.get_internal_type()=="DateField":
            fielddata["type"] = "text"
            fielddata["isDate"]=True
        elif field.get_internal_type()=="DateTimeField":
            fielddata["type"] = "text"
            fielddata["isDateTime"]=True     
        else:
            fielddata["type"] = "text"
            if isinstance(field, ForeignKey):
                if field.name in skip_related:
                    fields["text"].append(fielddata)
                    continue

                related_model = field.related_model
                related_key = field.name
                related_key_name = ""

                if hasattr(related_model, "defaultkey"):
                    related_key_name = related_model.defaultkey()
                    options = related_model.objects.filter(
                        domain_user_id=domain_user_id
                    ).values_list(
                        "id", related_key_name, related_model.defaultkey()
                    )
                else:
                    related_key_name = related_model._meta.pk.name
                    options = related_model.objects.filter(
                        domain_user_id=domain_user_id
                    ).values_list("id", related_key_name, "name")
                fielddata["options"] = [
                    {"id": option[0], "value": option[1]} for option in options
                ]
                fielddata["type"] = "select"
                field_defaults = model_to_dict(model_instance)
                fielddata["default"] = (
                    field_defaults[field.name] if field.name in field_defaults else ''
                )
        fields[fielddata["type"]].append(fielddata)
    return fields

def renderResponse(message, data, status=200):
    if status >= 200 and status < 300:
        return Response({
            "data": data,
            "message": message,
        }, status=status)
    else:
        if isinstance(data, dict):
            return Response({
                "errors": parseDictToList(data),
                "message": message,
            }, status=status)
        elif isinstance(data, list):
            return Response({
                "errors": data,
                "message": message,
            }, status=status)
        else:
            return Response({
                "errors": [data],
                "message": message,
            }, status=status)


def parseDictToList(data):
    values = []
    for key, value in data.items():
        values.extend(value)
    return values

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if isinstance(exc, AuthenticationFailed):
        response_data = {
            "message": exc.detail,
            "errors": exc.detail.get('messages', [])
        }
        return renderResponse(
            data=response_data['errors'], 
            message=response_data['message']["detail"],
            status=exc.status_code
        )
    elif isinstance(exc, NotAuthenticated):
        return renderResponse(
            data="User not authenticated",
            message="User not authenticated",
            status=exc.status_code
        )
    elif isinstance(exc, PermissionDenied):
        return renderResponse(
            data="You don't have permission to access this page",
            message="Permission Denied",
            status=exc.status_code
        )
    return response

class CustomPageNumberPagination(PageNumberPagination):
    page_size_query_param = "pageSize"
    max_page_size = 100



class CommonListAPIMixin:
    serializer_class = None
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        raise NotImplementedError("get_queryset not implemented")
    
    def common_list_decorator(serializer_class):
        def decorator(list_method):
            @wraps(list_method)
            def wrapped_list_method(self, request, *args, **kwargs):
                queryset = self.get_queryset()
                search_query = self.request.query_params.get('search', None)

                if search_query:
                    search_conditions = Q()

                    for field in serializer_class.Meta.model._meta.get_fields():
                        if isinstance(field, (models.CharField, models.TextField)):
                            search_conditions|=Q(**{f"{field.name}__icontains":search_query})
                    
                    queryset=queryset.filter(search_conditions)

                ordering=self.request.query_params.get("ordering", None)

                if ordering:
                    queryset=queryset.order_by(ordering)

                page = self.paginate_queryset(queryset)

                print(page)

                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    data=serializer.data
                    total_pages=self.paginator.page.paginator.num_pages
                    current_page=self.paginator.page.number
                    page_size=self.paginator.page.paginator.per_page
                    total_items=self.paginator.page.paginator.count
                else:
                    serializer = self.get_serializer(queryset, many=True)
                    data=serializer.data
                    total_pages=1
                    current_page=1
                    page_size=len(data)
                    total_items=len(data)

                return renderResponse(
                    data={
                        "data":data,
                    'totalPages': total_pages,
                    'totalItems': total_items,
                    'currentPage': current_page,
                    'pageSize': page_size
                    },
                    message="Data Retrieved Successfully",
                    status=200
                )
            return wrapped_list_method
        return decorator
    
# decorator for timestamp fields
def createParsedCreatedAtUpdatedAt(cls):
    cls.formatted_created_at=serializers.SerializerMethodField()
    cls.formatted_updated_at=serializers.SerializerMethodField()

    def get_formatted_created_at(self,obj):
        return obj.created_at.strftime('%dth %B %Y, %H:%M')
    
    def get_formatted_updated_at(self,obj):
        return obj.updated_at.strftime('%dth %B %Y, %H:%M')
    
    cls.get_formatted_created_at=get_formatted_created_at
    cls.get_formatted_updated_at=get_formatted_updated_at

    original_to_representation=cls.to_representation

    @wraps(original_to_representation)
    def to_representation(self,obj):
        representation=original_to_representation(self,obj)
        representation['created_at']=self.get_formatted_created_at(obj)
        representation['updated_at']=self.get_formatted_updated_at(obj)
        return representation
    
    cls.to_representation=to_representation
    return cls


class CommonListAPIMixinWithFilter:
    serializer_class = None
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        raise NotImplementedError("get_queryset not implemented")
    
    def common_list_decorator(serializer_class):
        def decorator(list_method):
            @wraps(list_method)
            def wrapped_list_method(self, request, *args, **kwargs):
                queryset = self.get_queryset()
                search_query = self.request.query_params.get('search', None)

                filtered_params = self.request.query_params.dict()
                key_to_remove = ['search', 'page', 'pageSize', 'ordering']
                for key in key_to_remove:
                    if key in filtered_params:
                        filtered_params.pop(key, None)
                
                if filtered_params:
                    search_conditions = Q()
                    for key, value in filtered_params.items():
                        ##search_conditions |= Q(**{f"{key}": value}) Or search
                        search_conditions &= Q(**{f"{key}": value}) # And search
                    queryset = queryset.filter(search_conditions)


                if search_query:
                    search_conditions = Q()

                    for field in serializer_class.Meta.model._meta.get_fields():
                        if isinstance(field, (models.CharField, models.TextField)):
                            search_conditions|=Q(**{f"{field.name}__icontains":search_query})
                    
                    queryset=queryset.filter(search_conditions)

                ordering=self.request.query_params.get("ordering", None)

                if ordering:
                    queryset=queryset.order_by(ordering)

                page = self.paginate_queryset(queryset)


                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    data=serializer.data
                    total_pages=self.paginator.page.paginator.num_pages
                    current_page=self.paginator.page.number
                    page_size=self.paginator.page.paginator.per_page
                    total_items=self.paginator.page.paginator.count
                else:
                    serializer = self.get_serializer(queryset, many=True)
                    data=serializer.data
                    total_pages=1
                    current_page=1
                    page_size=len(data)
                    total_items=len(data)
                
                EXCLUDE_FROM_FILTER_FIELDS = ['password', 
                                              'last_login', 
                                              'is_active', 
                                              'is_superuser',
                                                'is_staff',
                                                'date_joined',
                                                'social_media_links',
                                                'addition_details',
                                                'created_at',
                                                'updated_at',
                                                'last_ip',
                                                'last_device',
                                                'id',
                                                'quantity',
                                                'description',
                                                "whatsapp_number",
                                                'added_by_user_id',
                                              'email', 
                                              'image',
                                              'profile_pic',
                                              ]

                meta = serializer_class.Meta
                model_fields = meta.model._meta.fields

                fields = getattr(meta, "fields", [])
                if fields == "__all__":
                    fields = [f.name for f in model_fields]

                # Exclure les champs uniquement pour filterFields
                filter_fields_names = [f for f in fields if f not in EXCLUDE_FROM_FILTER_FIELDS]

                filterFields = [
                    {
                        "key": field.name,
                        "option": [
                            {"id": choice[0], "value": choice[1]} 
                            for choice in field.choices
                        ] if field.choices else None
                    }
                    for field in model_fields
                    if field.name in filter_fields_names
                ]


                return renderResponse(
                    data={
                    "filterFields": filterFields,
                    "data":data,
                    'totalPages': total_pages,
                    'totalItems': total_items,
                    'currentPage': current_page,
                    'pageSize': page_size
                    },
                    message="Data Retrieved Successfully",
                    status=200
                )
            return wrapped_list_method
        return decorator
    

def list_project_urls(patterns,parent_pattern=""):
    url_list=[]
    for pattern in patterns:
        if isinstance(pattern, URLPattern):
            url_list.append("/"+parent_pattern+str(pattern.pattern))
        elif isinstance(pattern, URLResolver):
            url_list.extend(list_project_urls(
                pattern.url_patterns, 
                parent_pattern=parent_pattern+str(pattern.pattern)
                )) 
    return url_list

def convertModeltoJSON(model):
    serialized_model = serialize('json', model)
    serializers_data = json.loads(serialized_model)
    modelItems=[]
    for data in serializers_data:
        data['fields']['id'] = data['pk']
        modelItems.append(data['fields'])
    return modelItems
    



def executeQuery(query, params):
    with connection.cursor() as cursor:
        cursor.execute(query, params)
        colums = [col[0] for col in cursor.description]
        return [dict(zip(colums, row)) for row in cursor.fetchall()]



def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
