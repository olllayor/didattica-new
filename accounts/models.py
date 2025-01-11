from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.models import EmailAddress
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os
import time


def profile_image_upload_path(instance, filename):
    # Generate a unique filename using the user's ID and a timestamp
    ext = os.path.splitext(filename)[1]  # Get the file extension
    new_filename = (
        f"{instance.user.username}_{instance.user.id}_{int(time.time())}{ext}"
    )
    return os.path.join("profile_images/", new_filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(
        upload_to=profile_image_upload_path, blank=True, null=True
    )
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

     # Add follow relationships
    followers = models.ManyToManyField(User, related_name="following", blank=True)
    following = models.ManyToManyField(User, related_name="followers", blank=True)


    

    def get_reaction_count(self):
        return self.reactions.count()
    
    def __str__(self):
        return f"@{self.user.username}"
    
    def get_followers_count(self):
        return self.followers.count()

    def get_following_count(self):
        return self.following.count()
    
    def get_reposts_count(self):
        return self.shares.count()

    def get_replies_count(self):
        return self.replies.count()


    def save(self, *args, **kwargs):
        # Only process the image if it's a new upload
        if self.profile_image and not self.pk:
            # Open the image using Pillow
            img = Image.open(self.profile_image)

            # Convert the image to RGB mode if it's not already
            if img.mode in ("RGBA", "LA"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(
                    img, mask=img.split()[-1]
                )  # Paste using alpha channel as mask
                img = background

            # Convert the image to WebP format with the best quality
            buffer = BytesIO()
            img.save(buffer, format="WEBP", quality=100)
            webp_image = ContentFile(buffer.getvalue())

            # Save the WebP image with the same name but with .webp extension
            filename = os.path.splitext(self.profile_image.name)[0] + ".webp"
            self.profile_image.save(filename, webp_image, save=False)

        super().save(*args, **kwargs)


# Signal to create a profile when a user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

