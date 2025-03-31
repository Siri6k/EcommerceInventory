from email import message
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

def index(request):
    return render(request, "index.html")


class FileUploadViewInS3(APIView):
    parser_classes=(MultiPartParser, FormParser)

    def post(self, request,*args, **kwargs):
        uploaded_files_urls=[]

        for file_key in request.FILES:
            file_obj=request.FILES[file_key]
            print(file_obj)
        
        return Response({
            'message':'File uploaded successfully',
            'urls':uploaded_files_urls
        },
            status = 200)