from django.urls import path
from . import views


urlpatterns = [
    path('', views.index),
    path('@<str:username>/', views.profile, name='profile'),
    path('search/', views.search, name='search'), 
    path('@<str:username>/follow/', views.follow_user, name='follow_user'),  # Add this line


]