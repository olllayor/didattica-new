from django.dispatch import receiver
from allauth.socialaccount.signals import pre_social_login
from .models import Profile

@receiver(pre_social_login)
def create_profile_if_needed(sender, request, sociallogin, **kwargs):
    """Ensure profile exists when social login occurs"""
    user = sociallogin.user
    if not hasattr(user, 'profile'):
        Profile.objects.get_or_create(user=user)