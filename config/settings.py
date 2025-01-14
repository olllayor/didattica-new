"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import boto3
from storages.backends.s3boto3 import S3Boto3Storage
load_dotenv()  # Load environment variables from .env file

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-5k8r#gac$aecqip)6=us5s1s_dw0-*516fjs(i-0nru*sytk^p"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["demo.jprq.site", "127.0.0.1"]
CSRF_TRUSTED_ORIGINS = ["https://olllayor.jprq.site", "https://demo.jprq.site"]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "debug_toolbar",
    "allauth_ui",  # Add this before allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "widget_tweaks",  # Add this
    "slippers",  # Add this
    "accounts",
    'community',
    "django.contrib.sites",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.telegram",
    "allauth.socialaccount.providers.twitter",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],  # Add this line
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

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
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

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR,'static')



# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


SITE_ID = 1
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_REDIRECT_URL = "/@<str:username>/"  # Redirect after successful login
LOGOUT_REDIRECT_URL = "/"  # Redirect after logout

ALLAUTH_UI_THEME = "cmyk"  # or "dark", "cupcake", etc.

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Use SMTP for production
# EMAIL_HOST = 'smtp.gmail.com'  # Replace with your SMTP server
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')  # Your email
# EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  # Your email password

# # Allauth settings
# ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_EMAIL_VERIFICATION = 'mandatory'  # Enforce email verification
# ACCOUNT_AUTHENTICATION_METHOD = 'username_email'  # Allow login with username or email
# ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1  # Email confirmation link expiry in days
# ACCOUNT_EMAIL_CONFIRMATION_COOLDOWN = 180  # Cooldown period in seconds
# ACCOUNT_LOGIN_ATTEMPTS_LIMIT = 5  # Limit login attempts
# ACCOUNT_LOGIN_ATTEMPTS_TIMEOUT = 300  # Timeout after failed login attempts
# ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True  # Logout user after password change





# Cloudflare R2 Configuration
CLOUDFLARE_R2_ACCESS_KEY_ID = os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID')  # Your R2 Access Key ID
CLOUDFLARE_R2_SECRET_ACCESS_KEY = os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY')  # Your R2 Secret Access Key
CLOUDFLARE_R2_BUCKET_NAME = os.getenv('CLOUDFLARE_R2_BUCKET_NAME')  # Your R2 Bucket Name
CLOUDFLARE_R2_ENDPOINT_URL = os.getenv('CLOUDFLARE_R2_ENDPOINT_URL')  # Your R2 Endpoint URL

# Django Storages Configuration
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = CLOUDFLARE_R2_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = CLOUDFLARE_R2_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME = CLOUDFLARE_R2_BUCKET_NAME
AWS_S3_ENDPOINT_URL = CLOUDFLARE_R2_ENDPOINT_URL
AWS_S3_CUSTOM_DOMAIN = f'{CLOUDFLARE_R2_BUCKET_NAME}.r2.cloudflarestorage.com'  # Optional: Use a custom domain
AWS_DEFAULT_ACL = 'public-read'  # Set ACL to public-read for public access
AWS_QUERYSTRING_AUTH = False  # Disable query string authentication for public files

# Media files configuration
MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/'  # URL to access media files
MEDIA_ROOT = ''  # Empty because files are stored in R2, not locally


SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
            "secret": os.getenv("GOOGLE_OAUTH_SECRET"),
            "key": "",
        },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    },
    "telegram": {
        "APP": {
            "client_id": os.getenv("TELEGRAM_CLIENT_ID"),
            "secret": os.getenv("TELEGRAM_CLIENT_SECRET"),
        },
        "AUTH_PARAMS": {
            "auth_date_validity": 30,  # Optional: Set expiration time in seconds
        },
    },
    "twitter": {
        "APP": {
            "client_id": os.getenv("TWITTER_OAUTH_CLIENT_ID"),
            "secret": os.getenv("TWITTER_OAUTH_SECRET"),
        }
    },
}

SOCIALACCOUNT_ADAPTER = 'accounts.adapter.CustomSocialAccountAdapter'