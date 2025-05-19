from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from boto3.session import Session
from EcommerceInventory.settings import (
    AWS_ACCESS_KEY_ID, 
    AWS_ACCESS_KEY_SECRET, 
    AWS_S3_REGION_NAME,
    AWS_STORAGE_BUCKET_NAME,
)
import os

from django.http import JsonResponse
from UserServices.models import Visit
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings

from django.core.cache import cache


def index(request):
    return render(request, "index.html")


class FileUploadViewInS3(APIView):
    parser_classes=(MultiPartParser, FormParser)

    def post(self, request,*args, **kwargs):
        uploaded_files_urls=[]

        for file_key in request.FILES:
            file_obj=request.FILES[file_key]
            s3_client=Session(
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_ACCESS_KEY_SECRET,
                region_name=AWS_S3_REGION_NAME
            ).client("s3")
        
            uniqueFileName=os.urandom(24).hex()+"_"+file_obj.name.replace(" ", "_")
            file_path="uploads/"+uniqueFileName

            s3_client.upload_fileobj(
                file_obj,
                AWS_STORAGE_BUCKET_NAME,
                file_path,
                ExtraArgs={
                    "ContentType":file_obj.content_type
                }
            )
            s3url=f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_path}"
            uploaded_files_urls.append(s3url)
        
        return Response({
            'message':'File uploaded successfully',
            'urls':uploaded_files_urls
        },
            status = 200)
    



# views.py


@require_POST
@csrf_exempt  # Only use this decorator if you've properly configured CORS
def save_visit(request):
    try:
        # Get client IP (handling proxy headers securely)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]  # Get first IP in case of multiple proxies
        else:
            ip_address = request.META.get('REMOTE_ADDR')


         # Rate limiting - 5 requests per IP per minute
        cache_key = f'visit_limit_{ip_address}'
        if cache.get(cache_key):
            return JsonResponse({'error': 'Too many requests. Please wait 1 minute.'}, status=429)
        cache.set(cache_key, True, timeout=60)  # 1 minute timeout
        
        # Parse JSON data safely
        try:
            data = json.loads(request.body)
            cookies = data.get('cookies', {})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        # Get User-Agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Validate data before saving
        if not ip_address:
            return JsonResponse({'error': 'Could not determine IP address'}, status=400)
        
        # Save to database
        Visit.objects.create(
            ip_address=ip_address,
            cookies=cookies,
            user_agent=user_agent
        )
        
        return JsonResponse({'message': 'Visit recorded successfully'}, status=201)
    
    except Exception as e:
        if settings.DEBUG:
            return JsonResponse({'error': str(e)}, status=500)
        return JsonResponse({'error': 'Internal server error'}, status=500)