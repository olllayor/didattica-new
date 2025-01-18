from django.core.management.base import BaseCommand
from django.conf import settings
import os
from PIL import Image
from io import BytesIO

class Command(BaseCommand):
    help = 'Create default profile images for new users'

    def generate_gradient_image(self, size, color1, color2):
        """Generate a gradient image"""
        image = Image.new('RGB', size)
        for y in range(size[1]):
            r = int(color1[0] * (1 - y/size[1]) + color2[0] * (y/size[1]))
            g = int(color1[1] * (1 - y/size[1]) + color2[1] * (y/size[1]))
            b = int(color1[2] * (1 - y/size[1]) + color2[2] * (y/size[1]))
            for x in range(size[0]):
                image.putpixel((x, y), (r, g, b))
        return image

    def handle(self, *args, **kwargs):
        # Create directory if it doesn't exist
        default_images_dir = os.path.join(settings.MEDIA_ROOT, 'default_profile_images')
        os.makedirs(default_images_dir, exist_ok=True)

        # Color combinations for gradients
        color_pairs = [
            ((255, 99, 107), (69, 204, 196)),    # Red to Turquoise
            ((111, 75, 255), (69, 183, 209)),    # Purple to Blue
            ((255, 107, 61), (255, 238, 173)),   # Orange to Yellow
            ((150, 203, 180), (255, 238, 173)),  # Green to Yellow
            ((255, 99, 107), (255, 238, 173)),   # Red to Yellow
            ((69, 183, 209), (150, 203, 180)),   # Blue to Green
            ((111, 75, 255), (255, 99, 107)),    # Purple to Red
            ((69, 204, 196), (255, 238, 173)),   # Turquoise to Yellow
        ]

        # Generate images
        for i, (color1, color2) in enumerate(color_pairs, 1):
            # Create gradient image
            img = self.generate_gradient_image((400, 400), color1, color2)
            
            # Save as WebP
            output_path = os.path.join(default_images_dir, f'default{i}.webp')
            img.save(output_path, 'WEBP', quality=95)
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created default{i}.webp')
            )

        self.stdout.write(
            self.style.SUCCESS('Successfully created all default profile images')
        )
