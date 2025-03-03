# community/models.py
import os
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image

User = get_user_model()


class Post(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("published", "Published"),
    ]
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="published"
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="posts/images/", blank=True, null=True)
    images = models.ManyToManyField(
        "PostImage", blank=True, related_name="posts_with_image"
    )
    file = models.FileField(upload_to="posts/files/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    views = models.PositiveIntegerField(default=0)
    # repost_of = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='reposts')  # Added field
    shared_post = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="shares"
    )
    reply_to = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="replies"
    )

    def __str__(self):
        return f"Post by {self.author.username}"

    def get_likes_count(self):
        return self.likes.count()

    def get_comments_count(self):
        return self.comments.count()

    def get_reaction_count(self):
        return self.reactions.count()

    def get_reposts_count(self):
        return (
            self.shares.count()
        )  # Count the number of times this post has been reposted

    def get_replies_count(self):
        return self.replies.count()
    
    def like(self, user):
        if user not in self.likes.all():
            self.likes.add(user)
            from notifications.signals import like_created
            like_created.send(sender=self.__class__, post=self, user=user)
            
    def unlike(self, user):
        """Remove a like"""
        if user in self.likes.all():
            self.likes.remove(user)
            
    class Meta:
        ordering = ['-created_at']


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_images")
    image = models.ImageField(upload_to="post_images/")

    def save(self, *args, **kwargs):
        if self.image:
            try:
                img = Image.open(self.image)
                if img.mode in ("RGBA", "LA"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                buffer = BytesIO()
                img.save(buffer, format="WEBP", quality=80)
                webp_image = ContentFile(buffer.getvalue())
                self.image.save(os.path.splitext(self.image.name)[0] + ".webp", webp_image, save=False)
            except Exception:
                # Add proper error handling/logging in production
                pass
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


class Reaction(models.Model):
    REACTION_CHOICES = [
        ("👍", "Thumbs Up"),
        ("😂", "Laugh"),
        ("🔥", "Fire"),
        ("👏", "Clap"),
        ("🚀", "Rocket"),
        # ('😲', 'Surprised'),
        # ('😡', 'Angry'),
        # ('💯', '100'),
        # ('👀', 'Eyes'),
        # ('🙌', 'Praise'),
        # ('🤔', 'Thinking'),
        # ('👎', 'Thumbs Down'),
        # ('🙏', 'Pray'),
        # ('🎉', 'Celebrate'),
        # ('🎵', 'Music'),
        # ('🎨', 'Art'),
        # ('📚', 'Books'),
        # ('💡', 'Lightbulb'),
        # ('🔗', 'Link'),
        # ('📸', 'Camera'),
        # ('🎥', 'Video'),
        # ('🔒', 'Lock'),
    ]
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reactions")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.CharField(max_length=2, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("post", "user")  # Ensure a user can only react once per post
