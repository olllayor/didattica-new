from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.core.exceptions import ValidationError
from allauth.socialaccount.forms import SignupForm
from allauth.socialaccount.helpers import complete_social_login
import re


class ProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)

    class Meta:
        model = Profile
        fields = ["username", "name", "profile_image", "website", "bio"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields["username"].initial = self.instance.user.username

    def clean_profile_image(self):
        image = self.cleaned_data.get("profile_image", False)
        if image:
            if image.size > 6 * 1024 * 1024:  # 4MB limit
                raise ValidationError("Image file too large ( > 6MB )")
            return image
        return None

    def clean_username(self):
        username = self.cleaned_data["username"]

        # Check format - must contain only lowercase letters, numbers, _, -, ', .
        if not re.match(r"^[a-z0-9_\-\.\']+$", username):
            raise forms.ValidationError(
                "Username can only contain lowercase letters, numbers, underscores, "
                "dashes, apostrophes, and periods (no spaces)."
            )

        # Check length (common requirement)
        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long.")

        # Check if username is taken (existing check)
        if (
            User.objects.filter(username=username)
            .exclude(pk=self.instance.user.pk)
            .exists()
        ):
            raise forms.ValidationError("This username is already taken.")

        return username

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.username = self.cleaned_data["username"]
        if commit:
            user.save()
            profile.save()
        return profile


class CustomSocialLoginForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add any custom initialization here
        for field in self.fields.values():
            field.widget.attrs["class"] = (
                "auth-input bg-black/30 border border-gray-700 rounded-lg p-3 w-full text-white placeholder-gray-500 focus:border-yellow-300/50"
            )

    def save(self, request):
        # Add any custom save logic here
        user = super().save(request)
        return user
