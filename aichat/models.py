import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class AIModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    model_id = models.CharField(max_length=100)
    logo_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    system_prompt = models.TextField(blank=True)

    # Updated Gemini-specific settings
    model_type_choices = [
        ("gemini-2.0-flash-exp", "Gemini 2.0 Flash"),
        ("learnlm-1.5-pro-experimental", "LearnLM 1.5 Pro Experimental"),
        ("gemini-1.5-pro", "Gemini 1.5 Pro"),
    ]
    model_type = models.CharField(
        max_length=100,  # Increased from 50 to 100 to safely accommodate all model IDs
        choices=model_type_choices,
        default="gemini-2.0-flash-exp",
    )
    safety_settings = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_default_prompt(self):
        return (
            "You are an AI tutor helping students prepare for exams. "
            "Analyze the question along with any images, provide an explanation "
            "of the concepts involved, and give a step-by-step solution. "
            "Use clear and simple language, suitable for students."
        )

    def get_safety_settings(self):
        return {
            "HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
            "HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
            "SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
            "DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE",
        }

    def get_generation_config(self):
        return {
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 40,
            "max_output_tokens": 2048,
        }


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="conversations"
    )
    ai_model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    last_message_at = models.DateTimeField(default=timezone.now)
    is_pinned = models.BooleanField(default=False)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.title or 'Untitled'} - {self.user.username}"

    def get_first_message(self):
        return self.messages.first()

    def update_title_from_first_message(self):
        first_message = self.get_first_message()
        if first_message and not self.title:
            # Truncate the message to create a title
            self.title = first_message.content[:50] + (
                "..." if len(first_message.content) > 50 else ""
            )
            self.save()

    def update_last_activity(self):
        self.last_message_at = timezone.now()
        self.save()

    def soft_delete(self):
        self.is_active = False
        self.save()


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    content = models.TextField()
    is_user = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    tokens_used = models.IntegerField(default=0)
    error = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{'User' if self.is_user else 'AI'}: {self.content[:50]}..."

    def mark_as_error(self, error_message):
        self.error = True
        self.content = error_message
        self.save()


class UserAPIToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    google_gemini_api_key = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_valid = models.BooleanField(default=True)
    monthly_token_usage = models.IntegerField(default=0)
    last_reset_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s API Token"

    def reset_monthly_usage(self):
        if timezone.now().month != self.last_reset_date.month:
            self.monthly_token_usage = 0
            self.last_reset_date = timezone.now()
            self.save()
