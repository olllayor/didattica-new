# community/models.py
from django.db import models
from django.contrib.auth import get_user_model
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os

User = get_user_model()

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="posts/images/", blank=True, null=True)
    images = models.ManyToManyField("PostImage", blank=True, related_name="posts_with_image")
    file = models.FileField(upload_to="posts/files/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Post by {self.author.username}"
    
    def get_likes_count(self):
        return self.likes.count()

    def get_comments_count(self):
        return self.comments.count()

class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_images")
    image = models.ImageField(upload_to="post_images/")

    def save(self, *args, **kwargs):
        if self.image:
            # Open the image using Pillow
            img = Image.open(self.image)
            
            # Convert the image to RGB mode if it's not already
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])  # Paste using alpha channel as mask
                img = background

            # Convert the image to WebP format with the best quality
            buffer = BytesIO()
            img.save(buffer, format='WEBP', quality=80)
            webp_image = ContentFile(buffer.getvalue())

            # Save the WebP image with the same name but with .webp extension
            self.image.save(
                os.path.splitext(self.image.name)[0] + '.webp',
                webp_image,
                save=False
            )

        super().save(*args, **kwargs)

class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent_comment = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username}"