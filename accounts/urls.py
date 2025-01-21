from django.urls import path
from . import views


urlpatterns = [
    path('', views.index),
    path('@<str:username>/', views.profile, name='profile'),
    path('search/', views.search, name='search'), 
    path('community/@<str:username>/follow/', views.follow_user, name='follow_user'),
    path('@<str:username>/followers/', views.followers_list, name='followers_list'),
    path('@<str:username>/following/', views.following_list, name='following_list'),


]