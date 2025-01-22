from django.urls import path
from . import views

urlpatterns = [
    # Chat routes
    path("chat/", views.chat_view, name="chat_view"),
    path("chat/conversation/", views.chat_conversation_view, name="chat_conversation_view"),
    path("chat/conversation/<uuid:conversation_id>/", views.chat_conversation_view, name="chat_conversation_detail"),
    path("chat/from-post/<int:post_id>/", views.chat_from_post, name="chat_from_post"),
    
    # API routes
    path("api/conversation/<uuid:conversation_id>/delete/", views.delete_conversation, name="delete_conversation"),
    path("api/conversation/<uuid:conversation_id>/title/", views.update_conversation_title, name="update_conversation_title"),
    path("api/settings/save/", views.save_settings, name="save_api_settings"),  # Updated name
    path("api/response/", views.get_ai_response, name="get_ai_response"),
    path("api/response/vision/", views.get_vision_response, name="get_vision_response"),
    path("api/models/", views.list_ai_models, name="list_ai_models"),
    path("api/feed/posts/", views.feed_posts_json, name="feed_posts_json"),
]
