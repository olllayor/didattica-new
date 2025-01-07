from django import forms
from .models import Post, PostImage, Comment
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class PostForm(forms.ModelForm):
    status = forms.ChoiceField(choices=Post.STATUS_CHOICES, initial='published', widget=forms.RadioSelect, required=False)
    images = MultipleFileField(required=False)

    class Meta:
        model = Post
        fields = ["content", "images", "file"]

    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get("content")
        images = self.files.getlist("images")  # Get list of uploaded images

        # If no content and no images, raise a validation error
        if not content and not images:
            raise forms.ValidationError("You must provide either text content or at least one image.")

        return cleaned_data

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
