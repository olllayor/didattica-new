from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import index

urlpatterns = [
    path('', index, name='index'),  # Root URL pattern
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # This includes all allauth URLs
    path('community/', include('community.urls')),
    path('', include('accounts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) if settings.DEBUG else []