from django.contrib import admin
from django.db.models import Sum
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import Chat, Message, MessageImage, UserProfile


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user_link",
        "title",
        "message_count",
        "total_tokens",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = ("user__username", "title")
    readonly_fields = ("created_at",)

    def user_link(self, obj):
        """Clickable link to user admin"""
        url = reverse("admin:auth_user_change", args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)

    user_link.short_description = "User"

    def message_count(self, obj):
        """Count messages in chat"""
        return obj.messages.count()

    message_count.short_description = "Messages"

    def total_tokens(self, obj):
        """Sum of tokens used in chat"""
        return (
            obj.messages.aggregate(Sum("tokens_consumed"))["tokens_consumed__sum"] or 0
        )

    total_tokens.short_description = "Total Tokens"

    fieldsets = (
        ("Basic Information", {"fields": ("user", "title")}),
        (
            "Statistics",
            {
                "fields": ("message_count", "total_tokens"),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at",),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "chat_link",
        "sender",
        "content_preview",
        "has_images",
        "tokens_consumed",
        "created_at",
    )
    list_filter = ("sender", "created_at")
    search_fields = ("content", "chat__title", "chat__user__username")
    readonly_fields = ("created_at", "tokens_consumed", "image_previews")

    def content_preview(self, obj):
        """Show preview of message content"""
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content

    content_preview.short_description = "Content Preview"

    def chat_link(self, obj):
        """Clickable link to chat admin"""
        url = reverse("admin:aichat_chat_change", args=[obj.chat.id])
        return format_html('<a href="{}">{}</a>', url, obj.chat.title)

    chat_link.short_description = "Chat"

    def has_images(self, obj):
        """Indicates if message has images"""
        return bool(obj.images.exists())

    has_images.boolean = True
    has_images.short_description = "Has Images"

    def image_previews(self, obj):
        """Shows all images associated with message"""
        images = obj.images.all()
        if not images:
            return "No images"
        return format_html(
            '<div style="display: flex; gap: 10px;">{}</div>',
            mark_safe(
                "".join(
                    f'<img src="{img.image.url}" style="max-width: 200px; height: auto;" />'
                    for img in images
                )
            ),
        )

    image_previews.short_description = "Images"

    fieldsets = (
        (
            "Message Information",
            {"fields": ("chat", "sender", "content", "tokens_consumed")},
        ),
        ("Images", {"fields": ("image_previews",)}),
        ("Timestamps", {"fields": ("created_at",), "classes": ("collapse",)}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "total_tokens_used",
        "tokens_remaining",
        "chat_count",
        "last_activity",
    )
    list_filter = ("created_at",)
    search_fields = ("user__username", "user__email")
    readonly_fields = (
        "created_at",
        "total_tokens_used",
        "tokens_remaining",
        "chat_count",
        "last_activity",
    )

    def total_tokens_used(self, obj):
        """Calculate total tokens used by user"""
        return (
            Message.objects.filter(chat__user=obj.user).aggregate(
                Sum("tokens_consumed")
            )["tokens_consumed__sum"]
            or 0
        )

    total_tokens_used.short_description = "Total Tokens Used"

    def tokens_remaining(self, obj):
        """Calculate remaining tokens"""
        return obj.token_limit - obj.tokens_used

    tokens_remaining.short_description = "Tokens Remaining"

    def chat_count(self, obj):
        """Count user's chats"""
        return Chat.objects.filter(user=obj.user).count()

    chat_count.short_description = "Total Chats"

    def last_activity(self, obj):
        """Get user's last message timestamp"""
        last_message = (
            Message.objects.filter(chat__user=obj.user).order_by("-created_at").first()
        )
        return last_message.created_at if last_message else "No activity"

    last_activity.short_description = "Last Activity"

    fieldsets = (
        ("User Information", {"fields": ("user",)}),
        (
            "Token Usage",
            {
                "fields": (
                    "token_limit",
                    "tokens_used",
                    "tokens_remaining",
                ),
            },
        ),
        (
            "Statistics",
            {
                "fields": ("total_tokens_used", "chat_count", "last_activity"),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at",), "classes": ("collapse",)},
        ),
    )


@admin.register(MessageImage)
class MessageImageAdmin(admin.ModelAdmin):
    list_display = ("id", "message_preview", "image_preview", "created_at")
    list_filter = ("created_at",)
    search_fields = ("message__content", "message__chat__title")
    readonly_fields = ("created_at", "image_preview")

    def message_preview(self, obj):
        """Show preview of parent message"""
        return (
            obj.message.content[:50] + "..."
            if len(obj.message.content) > 50
            else obj.message.content
        )

    message_preview.short_description = "Message"

    def image_preview(self, obj):
        """Show preview of the image"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 200px; height: auto;" />',
                obj.image.url,
            )
        return "No image"

    image_preview.short_description = "Image Preview"

    fieldsets = (
        ("Image Information", {"fields": ("message", "image", "image_preview")}),
        (
            "Timestamps",
            {
                "fields": ("created_at",),
                "classes": ("collapse",),
            },
        ),
    )

admin.site.site_header = "AI Chat Admin"
admin.site.site_title = "AI Chat Admin"
admin.site.index_title = "AI Chat Administration"




