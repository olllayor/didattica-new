from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    image = models.ImageField(upload_to="posts/images/", blank=True, null=True)
    images = models.ManyToManyField(
        "PostImage", blank=True, related_name="posts_with_image"
    )
    file = models.FileField(upload_to="posts/files/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post by {self.author.username}"


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


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_images")
    image = models.ImageField(upload_to="post_images/")
