from django import forms
from django.forms.widgets import ClearableFileInput

from .models import Chat, Message


class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        final_attrs = {"multiple": True, "accept": "image/*"}
        if attrs:
            final_attrs.update(attrs)
        super().__init__(attrs=final_attrs)


class ImageUploadForm(forms.Form):
    images = forms.FileField(widget=MultiFileInput(), required=False)
    chat_id = forms.IntegerField(required=True)


class ChatForm(forms.ModelForm):
    class Meta:
        model = Chat
        fields = ["title"]


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["content", "user_profile"]
        widgets = {"user_profile": forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields["user_profile"].initial = user.userprofile

    def save(self, *args, **kwargs):
        if not self.user_profile and self.chat:
            self.user_profile = self.chat.user.userprofile
        if self.sender == "user" and self.tokens_consumed > 0:
            self.user_profile.consume_tokens(self.tokens_consumed)
        super().save(*args, **kwargs)