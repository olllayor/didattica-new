from django.contrib import admin
from .models import Post, Comment, PostImage

# Register your models here.
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'content', 'created_at', 'updated_at')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'author__username')
    date_hierarchy = 'created_at'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'content', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'author__username')
    date_hierarchy = 'created_at'

@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ('post', 'image')
    list_filter = ('post',)
    search_fields = ('post__content',)