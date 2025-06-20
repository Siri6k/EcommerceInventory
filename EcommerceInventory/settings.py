"""
Django settings for EcommerceInventory project.

Generated by 'django-admin startproject' using Django 5.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from math import e
from operator import ge
from pathlib import Path
from datetime import timedelta

from dotenv import load_dotenv
import os

load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = ["*"]


# Application definition

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'django.contrib.sites',
]

# Third-party applications
# These are the apps that you have installed from third-party sources, such as PyPI or

THIRD_PARTY = [
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',# For social authentication
    'cloudinary', # For image upload
    'cloudinary_storage', # For image upload
    "rest_framework",
    'rest_framework.authtoken',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    "rest_framework_simplejwt",
    "corsheaders",
]
# Local applications
# These are the apps that you have created for your project

LOCALS_APPS = [
   "UserServices",
   "ProductServices",
   "InventoryServices",
   "OrderServices"
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY + LOCALS_APPS


SITE_ID = 1


AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Désactiver le modèle Token si on utilise uniquement JWT
DJ_REST_AUTH = {
    'USE_JWT': True,
    'TOKEN_MODEL': None,  # <-- empêche l'erreur d'import inutile du TokenModel
}

ACCOUNT_LOGIN_METHODS = {'email', 'username'}
ACCOUNT_SIGNUP_FIELDS = {
    'email': {'required': True},
    'username': {'required': True},
    'password': {'required': True},
}
# Configuration de django-allauth
ACCOUNT_EMAIL_VERIFICATION = 'none'

MIDDLEWARE = [
    
    "django.middleware.security.SecurityMiddleware",
    #Whitenoise for serving static files in production
    'whitenoise.middleware.WhiteNoiseMiddleware',
    #########
    "django.contrib.sessions.middleware.SessionMiddleware",
     # Your other middlewares...
    "corsheaders.middleware.CorsMiddleware",  
    # Make sure it's before 'CommonMiddleware'
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    'allauth.account.middleware.AccountMiddleware',
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    # Your other middlewares...
    "EcommerceInventory.middleware.PermissionMiddleware.PermissionMiddleware",
    "UserServices.middleware.UsersLogsMiddleware.UpdateLastLoginMiddleware",

]


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': GOOGLE_CLIENT_ID,
            'secret': GOOGLE_CLIENT_SECRET,
            'key': '',
        }
    }
}


REST_FRAMEWORK = {
   
    "EXCEPTION_HANDLER": "EcommerceInventory.Helpers.custom_exception_handler",
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# Allow requests from your frontend (localhost:3000 in this case)
CORS_ORIGIN_WHITELIST = [
    "http://localhost:3000",
    "https://niplan-market.onrender.com",
    "http://ec2-13-233-173-206.ap-south-1.compute.amazonaws.com"
]

CORS_ORIGIN_WHITELIST += [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://niplan-market.onrender.com",
    "http://ec2-13-233-173-206.ap-south-1.compute.amazonaws.com",
]


ROOT_URLCONF = "EcommerceInventory.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": ['EcommerceInventory/templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "EcommerceInventory.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
dbhost = os.getenv('DATABASE_HOST')
dbname = os.getenv('DATABASE_NAME')
dbuser = os.getenv('DATABASE_USER')
dbpassword = os.getenv('DATABASE_PASSWORD')

if DEBUG:
   dbhost = 'localhost'
   dbname = 'ecommerce'
   dbuser = 'ecommerce'
   dbpassword = 'test123456@cool'
   
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": dbname,  
        "USER": dbuser,         # Default user
        "PASSWORD": dbpassword,     # Default empty password
        "HOST": dbhost,
        "PORT": os.getenv('DATABASE_PORT'),         # Default port
    }
}




# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
    ]

# Enable compression and caching for Whitenoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
AUTH_USER_MODEL = "UserServices.Users"

REST_USE_JWT = True


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),  # 1 day
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),  # 7 days
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),  # 1 day
    "TOKEN_OBTAIN_SERIALIZER": "UserServices.serializers.MyTokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "UserServices.serializers.MyTokenRefreshSerializer",
}

# AWS S3 settings
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_ACCESS_KEY_SECRET = os.getenv('AWS_ACCESS_KEY_SECRET')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')

# Cloudinary settings
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),    
}

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
