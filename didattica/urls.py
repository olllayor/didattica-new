from django.urls import path, include

urlpatterns = [
    # ...existing urls...
    path('ai/', include('ai.urls', namespace='ai')),
]