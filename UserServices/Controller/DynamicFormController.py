import re

from django.shortcuts import render
from EcommerceInventory.Helpers import (
    getDynamicFormModels,
    getDynamicFormFields,
    getExcludeFields,
    renderResponse,
)


from dateutil.parser import parse as parse_date
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from django.core.serializers import serialize
import json
from django.apps import apps

from UserServices.models import Users

from django.db import models


class DynamicFormController(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, modelName, id=None):
        # Checking if model Name exists in the models
        if modelName not in getDynamicFormModels():
            return renderResponse(
                data="Model Not Exist", message="Model Not Exist", status=404
                )
        # getting the model name from the models
        model = getDynamicFormModels()[modelName]
        model_class = apps.get_model(model)

        if model_class is None:
            return renderResponse(
                data="Model Not Found", message="Model Not Found", status=404
            )
            

        field_info = model_class._meta.fields
        model_fields = [field.name for field in field_info]
        exclude_fields = getExcludeFields()

        required_fields = [
            field.name
            for field in field_info
            if not field.null
            and field.default == models.NOT_PROVIDED
            and field.name not in exclude_fields
        ]

        missing_fields = [
            field for field in required_fields if field not in request.data
        ]
        if missing_fields:
            return renderResponse(
                data=[
                    f"Thefollowing field in required: {field}"
                    for field in missing_fields
                ],
                message="Validation Error", 
                status=400
            ),
           
        # creating a copy of post data
        fields = request.data.copy()
       

        fieldsdata = {
            key: value for key, value in fields.items() if key in model_fields
        }
        # all the model fields data
        print(model_fields)
        # all the post data fields
        print(fields.items())
        # sanititizing the post data fields by model fields data and eliminating the extra fields
        print(fieldsdata.items())

        # assigning Foreign Key instance for ForeignKey fields in Post Data
        for field in field_info:
            if (
                field.is_relation
                and field.name in fieldsdata
                and isinstance(fieldsdata[field.name], int)
            ):
                related_model = field.related_model
                try:
                    fieldsdata[field.name] = related_model.objects.get(
                        id=fieldsdata[field.name]
                    )
                except related_model.DoesNotExist:
                    return renderResponse(
                        data=f"{field.name} Relation Not Exist Found",
                        message=f"{field.name} Relation Not Exist Found",
                        status=404
                    )
            # allow empty foreign key on post data
            elif field.is_relation and field.name in fieldsdata:
                fieldsdata.pop(field.name)

         # Nettoyage des champs spéciaux (date, datetime, etc.)
        for field in field_info:
            if field.name in fieldsdata:
                value = fieldsdata[field.name]

                # Convertir chaînes vides en None pour champs date
                if isinstance(field, (models.DateField, models.DateTimeField)):
                    if value == "":
                        fieldsdata[field.name] = None
                    elif isinstance(value, str):
                        try:
                            # Essayons de parser la date
                            parsed_value = parse_date(value)
                            fieldsdata[field.name] = parsed_value
                        except Exception:
                            return renderResponse(
                                data=f"Invalid date format for field: {field.name}",
                                message="Validation Error",
                                status=400
                            )


          
        fieldsdata["domain_user_id"] = request.user.domain_user_id        
        fieldsdata["added_by_user_id"] = Users.objects.get(id=request.user.id)



        # Handle empty date strings
        
        # checking if the model instance exists or not
        if id:
            model_instance = model_class.objects.filter(
                id=id, 
                domain_user_id=request.user.domain_user_id
            )
            if not model_instance.exists():
                return renderResponse(
                    data='ModelItem Not Found',
                    message='Model Item Not Found',
                    status=404
                )
            model_instance = model_instance.first()
            if "password" in fieldsdata:
                model_instance.set_password(fieldsdata["password"])
                del fieldsdata["password"]

            # Attribuer les autres champs
            for key, value in fieldsdata.items():
                setattr(model_instance, key, value)

            model_instance.save()
        else:
            model_instance = model_class.objects.create(**fieldsdata)

        serialized_data = serialize("json", [model_instance])
        model_json = json.loads(serialized_data)
        response_json = model_json[0]["fields"]
        response_json["id"] = model_json[0]["pk"]

       
        return renderResponse(
            data=response_json, 
            message="Data saved successfully", 
            status=201
        )
        
####################################################

    def get(self, request, modelName, id=None):
        if modelName not in getDynamicFormModels():
            return renderResponse(
                data="Model Not Exist", 
                message="Model Not Exist", 
                status=404
            )
        model = getDynamicFormModels()[modelName]
        model_class = apps.get_model(model)

        if model_class is None:
            return renderResponse(
                data="Model Not Found", 
                message="Model Not Found", 
                status=404
            )
        
        if id:
            model_instance = model_class.objects.filter(
                id=id, 
                domain_user_id=request.user.domain_user_id
            )
            if model_instance.exists():
                model_instance = model_instance.first()
            else:
                return renderResponse(
                    data='ModelItem Not Found',
                    message='Model Item Not Found',
                    status=404
                )

        else:
            model_instance = model_class()

        fields = getDynamicFormFields(
            model_instance, request.user.domain_user_id)
        
        return renderResponse(
            data=fields, 
            message="Form fetched successfully"
        )
      