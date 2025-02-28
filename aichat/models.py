from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chats")
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    class Meta:
        ordering = ["-created_at"]


class Message(models.Model):
    SENDER_CHOICES = [
        ("user", "User"),
        ("ai", "AI"),
        ("system", "System"),
    ]

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    tokens_consumed = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    user_profile = models.ForeignKey(
        "UserProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="messages",
    )

    def __str__(self):
        return f"{self.sender} message in {self.chat.title}"

    class Meta:
        ordering = ["created_at"]


class MessageImage(models.Model):
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="message_images/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for message {self.message.id}"

    class Meta:
        ordering = ["-created_at"]


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token_limit = models.IntegerField(default=100000)  # Daily token limit
    tokens_used = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    last_token_reset = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Profile for {self.user.username}"

    def has_enough_tokens(self, requested_tokens):
        """Check if user has enough tokens for the request"""
        return (self.tokens_used + requested_tokens) <= self.token_limit

    def consume_tokens(self, amount):
        """Consume tokens and update the count"""
        self.tokens_used += amount
        self.save()

    def reset_tokens_if_needed(self):
        """Reset tokens if it's a new day"""
        now = timezone.now()
        if self.last_token_reset.date() < now.date():
            self.tokens_used = 0
            self.last_token_reset = now
            self.save()


@receiver(post_save, sender=User)
def create_user_profile_for_chat(sender, instance, created, **kwargs):
    """Create a UserProfile when a new user is created"""
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile_for_chat(sender, instance, **kwargs):
    """Ensure UserProfile exists and is saved"""
    if not hasattr(instance, 'userprofile'):
        UserProfile.objects.create(user=instance)
    instance.userprofile.save()
