import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-5k8r#gac$aecqip)6=us5s1s_dw0-*516fjs(i-0nru*sytk^p"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]
CSRF_TRUSTED_ORIGINS = ["https://*.jprq.site"]

# Application definition

INSTALLED_APPS = [
    "channels",  # Add this
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "webpush",  # Add this
    "debug_toolbar",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "widget_tweaks",
    "slippers",
    "accounts",
    "community",
    "aichat",
    "notifications",
    "django.contrib.sites",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.telegram",
    "allauth.socialaccount.providers.twitter",
]

MIDDLEWARE = [
    "api_analytics.django.Analytics",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django_user_agents.middleware.UserAgentMiddleware",
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
                "notifications.context_processors.notification_count",  # Add this line
            ],
        },
    },
]

ASGI_APPLICATION = "config.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],  # Adjust if using a Redis service
        },
    },
}

WSGI_APPLICATION = "config.wsgi.application"

INTERNAL_IPS = ["127.0.0.1"]


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


STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
            "secret": os.getenv("GOOGLE_OAUTH_SECRET"),
            "key": "",
        },
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
        "OAUTH_PKCE_ENABLED": True,
    },
    "telegram": {
        "APP": {
            "client_id": os.getenv("TELEGRAM_CLIENT_ID"),
            "secret": os.getenv("TELEGRAM_CLIENT_SECRET"),
        },
        "AUTH_PARAMS": {
            "auth_date_validity": 30,
        },
    },
    "twitter": {
        "APP": {
            "client_id": os.getenv("TWITTER_OAUTH_CLIENT_ID"),
            "secret": os.getenv("TWITTER_OAUTH_SECRET"),
        },
        "OAUTH_PKCE_ENABLED": True,
    },
}

SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_PROVIDERS_CALLBACK_URL = "accounts/%(provider)s/login/callback/"
SOCIALACCOUNT_TEMPLATE_EXTENSION = "html"
SOCIALACCOUNT_FORMS = {
    "login": "accounts.forms.CustomSocialLoginForm",
}

SOCIALACCOUNT_ADAPTER = "accounts.adapter.CustomSocialAccountAdapter"

# Add these settings for social account handling
SOCIALACCOUNT_AUTO_SIGNUP = True  # Enable automatic signup
SOCIALACCOUNT_EMAIL_REQUIRED = False  # Make email optional for social signup
ACCOUNT_USERNAME_REQUIRED = False  # Make username optional initially

ANALYTICS_API_KEY = "4fba4480-104f-409b-a10a-8db9e4f9a95e"


# Cloudflare R2 Configuration
# CLOUDFLARE_R2_ACCESS_KEY_ID = os.getenv('CLOUDFLARE_R2_ACCESS_KEY_ID')  # Your R2 Access Key ID
# CLOUDFLARE_R2_SECRET_ACCESS_KEY = os.getenv('CLOUDFLARE_R2_SECRET_ACCESS_KEY')  # Your R2 Secret Access Key
# CLOUDFLARE_R2_BUCKET_NAME = os.getenv('CLOUDFLARE_R2_BUCKET_NAME')  # Your R2 Bucket Name
# CLOUDFLARE_R2_ENDPOINT_URL = os.getenv('CLOUDFLARE_R2_ENDPOINT_URL')  # Your R2 Endpoint URL

# # Django Storages Configuration
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# AWS_ACCESS_KEY_ID = CLOUDFLARE_R2_ACCESS_KEY_ID
# AWS_SECRET_ACCESS_KEY = CLOUDFLARE_R2_SECRET_ACCESS_KEY
# AWS_STORAGE_BUCKET_NAME = CLOUDFLARE_R2_BUCKET_NAME
# AWS_S3_ENDPOINT_URL = CLOUDFLARE_R2_ENDPOINT_URL
# AWS_S3_CUSTOM_DOMAIN = f'{CLOUDFLARE_R2_BUCKET_NAME}.r2.cloudflarestorage.com'  # Optional: Use a custom domain
# AWS_DEFAULT_ACL = 'public-read'  # Set ACL to public-read for public access
# AWS_QUERYSTRING_AUTH = False  # Disable query string authentication for public files

# # Media files configuration
# MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/'  # URL to access media files
# MEDIA_ROOT = ''  # Empty because files are stored in R2, not locally

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

# # Allauth customization
# ACCOUNT_AUTHENTICATION_METHOD = "username_email"
# ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_EMAIL_VERIFICATION = "mandatory"
# ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = True
# ACCOUNT_USERNAME_MIN_LENGTH = 4
# LOGIN_REDIRECT_URL = "feed"
# ACCOUNT_LOGOUT_REDIRECT_URL = "index"

# # Template customization
# ACCOUNT_TEMPLATE_EXTENSION = 'html'
# ACCOUNT_TEMPLATE_DIR = 'account'  # This tells allauth to look in the templates/account directory

# Add these settings for logout handling
ACCOUNT_LOGOUT_ON_GET = False  # Require POST request for logout
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True  # Logout after password change
ACCOUNT_LOGOUT_REDIRECT_URL = "/"  # Where to redirect after logout

LOGIN_URL = "/accounts/login/"
