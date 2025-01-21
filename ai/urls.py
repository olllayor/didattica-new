from django.urls import path
from . import views

app_name = 'ai'

urlpatterns = [
    path('chat/', views.chat_view, name='chat'),
    path('check-device/', views.check_device, name='check_device'),
]
