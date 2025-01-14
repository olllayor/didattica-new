from django.contrib import admin
from .models import Post, Comment, PostImage, Reaction

# Inline admin for PostImage
class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 1
    fields = ('image', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 100px; max-width: 100px;" />'
        return "No Image"
    image_preview.allow_tags = True
    image_preview.short_description = 'Preview'

# Inline admin for Comment
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1
    fields = ('author', 'content', 'created_at')
    readonly_fields = ('created_at',)

# Inline admin for Reaction
class ReactionInline(admin.TabularInline):
    model = Reaction
    extra = 1
    fields = ('user', 'reaction', 'created_at')
    readonly_fields = ('created_at',)

# Custom PostAdmin
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'content_preview', 'status', 'created_at', 'updated_at', 'likes_count', 'views_count', 'comments_count', 'reactions_count')
    list_filter = ('status', 'created_at', 'author')
    search_fields = ('content', 'author__username')
    date_hierarchy = 'created_at'
    inlines = [PostImageInline, CommentInline, ReactionInline]
    readonly_fields = ('created_at', 'updated_at', 'likes_count', 'views_count', 'comments_count', 'reactions_count')

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

    def likes_count(self, obj):
        return obj.likes.count()
    likes_count.short_description = 'Likes'

    def views_count(self, obj):
        return obj.views
    views_count.short_description = 'Views'

    def comments_count(self, obj):
        return obj.comments.count()
    comments_count.short_description = 'Comments'

    def reactions_count(self, obj):
        return obj.reactions.count()
    reactions_count.short_description = 'Reactions'

# Custom CommentAdmin
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post_preview', 'content_preview', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'author__username', 'post__content')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

    def post_preview(self, obj):
        return obj.post.content[:50] + '...' if len(obj.post.content) > 50 else obj.post.content
    post_preview.short_description = 'Post'

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'

# Custom PostImageAdmin
@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    list_display = ('post_preview', 'image_preview')
    list_filter = ('post',)
    search_fields = ('post__content',)

    def post_preview(self, obj):
        return obj.post.content[:50] + '...' if len(obj.post.content) > 50 else obj.post.content
    post_preview.short_description = 'Post'

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 100px; max-width: 100px;" />'
        return "No Image"
    image_preview.allow_tags = True
    image_preview.short_description = 'Preview'

# Custom ReactionAdmin
@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'post_preview', 'reaction', 'created_at')
    list_filter = ('reaction', 'created_at', 'user')
    search_fields = ('post__content', 'user__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

    def post_preview(self, obj):
        return obj.post.content[:50] + '...' if len(obj.post.content) > 50 else obj.post.content
    post_preview.short_description = 'Post'