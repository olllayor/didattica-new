from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_post, name="create_post"),
    path("feed/", views.feed, name="feed"),
    path("post/<int:post_id>/comment/", views.add_comment, name="add_comment"),
]
