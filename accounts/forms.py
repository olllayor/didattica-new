from django import forms
from django.contrib.auth.models import User
from .models import Profile
from django.core.exceptions import ValidationError


class ProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)

    class Meta:
        model = Profile
        fields = ['username', 'profile_image', 'website', 'bio']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['username'].initial = self.instance.user.username

    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image', False)
        if image:
            if image.size > 6 * 1024 * 1024:  # 4MB limit
                raise ValidationError("Image file too large ( > 6MB )")
            return image
        return None

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exclude(pk=self.instance.user.pk).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.username = self.cleaned_data['username']
        if commit:
            user.save()
            profile.save()
        return profile