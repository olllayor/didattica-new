from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User
import random
import string

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)

        # Generate a unique username if not provided
        if not user.username:
            user.username = self.generate_unique_username(sociallogin)
            user.save()

        return user

    def generate_unique_username(self, sociallogin):
        # Use the email or provider-specific ID to generate a username
        email = sociallogin.account.extra_data.get('email', '')
        provider = sociallogin.account.provider

        if provider == 'google':
            # Use the email prefix (before @) as the username
            username = email.split('@')[0]
        elif provider == 'telegram':
            # Use the Telegram username or ID
            username = sociallogin.account.extra_data.get('username', '')
            if not username:
                username = f"telegram_{sociallogin.account.uid}"
        else:
            # Fallback: Generate a random username
            username = f"user_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"

        # Ensure the username is unique
        if User.objects.filter(username=username).exists():
            username = f"{username}_{random.randint(1000, 9999)}"

        return username