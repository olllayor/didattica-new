from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_post, name="create_post"),
    path("feed/", views.feed, name="feed"),
    path("post/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path("post/<int:post_id>/like/", views.like_post, name="like_post"),
    path(
        "post/<int:post_id>/check_like/", views.check_like, name="check_like"
    ),  # Add this line
    path("post/<int:post_id>/", views.post_detail, name="post_detail"),
    path("post/<int:post_id>/share/", views.share_post, name="share_post"),
    path("post/<int:post_id>/react/", views.react_to_post, name="react_to_post"),
]
