import logging
import random
import string

import requests
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import User
from django.core.files.base import ContentFile

from .models import Profile

logger = logging.getLogger(__name__)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        This method is called before the social login process is completed.
        We can use it to check if the user already exists, and if not, create a new user.
        """
        try:
            user = sociallogin.user
            if user.id:  # If the user already exists, do nothing
                return

            # Check if a user with the same email already exists
            email = sociallogin.account.extra_data.get("email", "")
            if email:
                try:
                    existing_user = User.objects.get(email=email)
                    sociallogin.connect(request, existing_user)
                    return
                except User.DoesNotExist:
                    pass

            # Generate a unique username if not provided
            if not user.username:
                user.username = self.generate_unique_username(sociallogin)

            # Set a default password (since social login doesn't provide one)
            user.set_unusable_password()

            # Save the user
            user.save()

            # Ensure the profile exists
            profile, created = Profile.objects.get_or_create(user=user)

            if created:
                provider = sociallogin.account.provider
                extra_data = sociallogin.account.extra_data

                # Try to get provider's profile image
                profile_image_url = None
                if provider == "google":
                    profile_image_url = extra_data.get("picture")
                elif provider == "telegram":
                    profile_image_url = extra_data.get("photo_url")
                elif provider == "twitter":
                    profile_image_url = extra_data.get("profile_image_url_https")

                if profile_image_url:
                    try:
                        response = requests.get(profile_image_url)
                        if response.status_code == 200:
                            # Save the downloaded image
                            file_name = f"profile_{user.username}.webp"
                            profile.profile_image.save(
                                file_name, ContentFile(response.content), save=True
                            )
                    except Exception as e:
                        logger.error(f"Error downloading profile image: {e}")
                        # If failed to download, a default image will be used

        except Exception as e:
            logger.error(f"Error in pre_social_login: {e}")

    def generate_unique_username(self, sociallogin):
        """
        Generate a unique username based on the provider's data.
        """
        email = sociallogin.account.extra_data.get("email", "")
        provider = sociallogin.account.provider

        if provider == "google":
            # Use the email prefix (before @) as the username
            username = email.split("@")[0]
        elif provider == "telegram":
            # Use the Telegram username or ID
            username = sociallogin.account.extra_data.get("username", "")
            if not username:
                username = f"telegram_{sociallogin.account.uid}"
        else:
            # Fallback: Generate a random username
            username = f"user_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"

        # Ensure the username is unique
        if User.objects.filter(username=username).exists():
            username = f"{username}_{random.randint(1000, 9999)}"

        return username
