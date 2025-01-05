from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"@{self.user.username}"
    
    def save(self, *args, **kwargs):
        if self.profile_image:
            # Open the image using Pillow
            img = Image.open(self.profile_image)
            
            # Convert the image to RGB mode if it's not already
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])  # Paste using alpha channel as mask
                img = background

            # Convert the image to WebP format with the best quality
            buffer = BytesIO()
            img.save(buffer, format='WEBP', quality=100)
            webp_image = ContentFile(buffer.getvalue())

            # Save the WebP image with the same name but with .webp extension
            self.profile_image.save(
                os.path.splitext(self.profile_image.name)[0] + '.webp',
                webp_image,
                save=False
            )

        super().save(*args, **kwargs)

# Signal to create a profile when a user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()