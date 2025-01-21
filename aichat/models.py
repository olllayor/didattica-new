from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class AIModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    model_id = models.CharField(max_length=100)  # For OpenRouter model identifier
    logo_url = models.URLField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class UserAPIToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    openrouter_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s API Token"

