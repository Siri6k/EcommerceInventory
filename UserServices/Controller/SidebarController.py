from django.urls import get_resolver
from EcommerceInventory.permission import IsSuperAdmin
from EcommerceInventory.Helpers import (
    convertModeltoJSON, 
    list_project_urls, 
    renderResponse
)
from rest_framework import generics
from UserServices.models import ModuleUrls, Modules, UserPermissions
import json
from django.core.serializers import serialize as serializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class ModuleView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        permission_module_ids=[]
        #return all modules for super Admin and Top Domain level User
        if request.user.role == 'Super Admin' or (request.user.domain_user_id and request.user.domain_user_id.id==request.user.id):
            menus = Modules.objects.filter(
                is_menu=True, parent_id=None
                ).order_by('display_order')
        else:
            permission_module_ids=UserPermissions.objects.filter(
                user=request.user,
                is_permission=True
            ).values_list('module_id', flat=True)

            menus = Modules.objects.filter(
                is_menu=True, parent_id=None
                ).filter(id__in=permission_module_ids).order_by('display_order')

        serialized_menus = serializer('json', menus)

        serialized_menus = json.loads(serialized_menus)

        cleaned_menus= []
        for menu in serialized_menus:
            menu["fields"]["id"] = menu["pk"]
            if request.user.role == 'Super Admin' or (request.user.domain_user_id and request.user.domain_user_id.id==request.user.id):
                menu["fields"] ["submenus"]= Modules.objects.filter(
                    parent_id=menu["pk"], is_menu=True, is_active=True
                    ).order_by('display_order').values(
                        'id', "module_name", "module_url", 
                        "module_icon", 
                        "module_description",
                        "display_order", "is_menu", 
                        "is_active", "parent_id"
                        )
            else:
                 menu["fields"] ["submenus"]= Modules.objects.filter(
                    parent_id=menu["pk"], is_menu=True, is_active=True
                    ).filter(id__in=permission_module_ids) \
                     .order_by('display_order') \
                     .values(
                        'id', "module_name", "module_url", 
                        "module_icon", 
                        "module_description",
                        "display_order", "is_menu", 
                        "is_active", "parent_id"
                     )

            cleaned_menus.append(menu["fields"])
        if request.user.role == "Super Admin":
            cleaned_menus.append({
                    'id':0,
                    'module_name':"Manage Modules Urls",
                    'module_icon':'',
                    'is_menu': True,
                    "is_active":True,
                    'parent_id':None,
                    "display_order":0,
                    'module_url':"/manage/moduleUrls/",
                    "module_description":"Module Urls",
                    "submenus":[],
                 })

        return renderResponse(
            data=cleaned_menus, 
            message='All Modules', 
            status=200
        )
    
class ModuleUrlsListAPIView(APIView):
    authentication_classes = [JWTAuthentication] 
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        urls = ModuleUrls.objects.all()
        urlJson = convertModeltoJSON(urls)

        urlconf = get_resolver()
        urlsProject = list_project_urls(urlconf.url_patterns)

        modules = Modules.objects.all()
        modulesJson = convertModeltoJSON(modules)
        modulesJson.insert(0,{
            "id": 0,
            "module_name": "Skip Permission",
            
        })

        return renderResponse(
            data={
                "moduleUrls": urlJson,
                "project_urls": urlsProject,
                "modules": modulesJson
            },
            message='All Module URLs',
            status=200
        )
    
    def post(self, request):
        data = request.data
        for item in data:
            if item["url"] != None:
                if ModuleUrls.objects.filter(url=item["url"]).exists():
                    moduleUrl = ModuleUrls.objects.get(url=item["url"])
                    item["id"] = moduleUrl.id
                if "id" in item and item["id"] and item["id"] != 0:
                    moduleUrl = ModuleUrls.objects.get(id=item["id"])
                    moduleUrl.url = item["url"]
                else:
                    moduleUrl = ModuleUrls(url=item["url"])

                if item['module']!=0 and item['module']!=None:
                    moduleUrl.module = Modules.objects.get(id=item["module"])
                moduleUrl.save()
        return renderResponse(
            data={}, 
            message='Module URLs Created/Updated', 
            status=200
        )