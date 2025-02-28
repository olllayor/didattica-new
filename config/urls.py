from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import index
from debug_toolbar.toolbar import debug_toolbar_urls
from django.http import HttpResponse


def health_check(request):
    return HttpResponse("OK")



urlpatterns = (
    [
        path("", index, name="index"),  # Root URL pattern
        path("admin/", admin.site.urls),
        path("accounts/", include("allauth.urls")),  # This includes all allauth URLs
        path("home/", include("community.urls")),
        path("", include("accounts.urls")),
        path("ai/", include("aichat.urls")),
        path("notifications/", include("notifications.urls")),
        path("health/", health_check, name="health_check"),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if settings.DEBUG
    else []
)

if settings.DEBUG:
    urlpatterns += debug_toolbar_urls()
