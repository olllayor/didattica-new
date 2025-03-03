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
            return [single_file_clean(d, initial) for d in data]
        return single_file_clean(data, initial)

class PostForm(forms.ModelForm):
    status = forms.ChoiceField(choices=Post.STATUS_CHOICES, initial='published', widget=forms.RadioSelect, required=False)
    images = MultipleFileField(required=False)  # Handles multiple images
    image = forms.ImageField(required=False)    # Handles single image
    reply_to = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    shared_post = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Post
        fields = ["content", "image", "images", "file", "status", "reply_to", "shared_post"]

    def clean(self):
        cleaned_data = super().clean()
        content = cleaned_data.get("content")
        image = cleaned_data.get("image")
        images = self.files.getlist("images")

        # Require at least some content (text or images)
        if not content and not image and not images:
            raise forms.ValidationError("You must provide either text content or at least one image.")
        return cleaned_data

    def save(self, commit=True):
        post = super().save(commit=False)
        if commit:
            post.save()
            # Handle single image
            if self.cleaned_data.get('image'):
                post.image = self.cleaned_data['image']
                post.save()
            # Handle multiple images
            for image in self.files.getlist('images'):
                PostImage.objects.create(post=post, image=image)
        return post

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
