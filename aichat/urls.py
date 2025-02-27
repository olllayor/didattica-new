from django.http import JsonResponse
from django.urls import path
from django.views.decorators.http import require_GET

from . import views


@require_GET
def check_auth(request):
    """Check if user is authenticated"""
    if request.user.is_authenticated:
        return JsonResponse(
            {
                "authenticated": True,
                "username": request.user.username,
                "user_id": request.user.id,
            }
        )
    return JsonResponse(
        {
            "authenticated": False,
            "login_url": "/accounts/login/?next=/ai/",  # Add explicit login URL
        },
        status=401,
    )


urlpatterns = [
    # Main views
    path("", views.index, name="ai"),
    # Authentication endpoints
    path("auth/check/", check_auth, name="auth_check"),
    # Chat endpoints
    path("chat/", views.ask_gemini_chat, name="ask_gemini_chat"),
]