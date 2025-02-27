# utils.py
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile


def convert_image_to_webp(image_file):
    """
    Convert an image file to WEBP format.
    """
    # Open the image using Pillow.
    image = Image.open(image_file)

    # Convert image to RGB if not already (WEBP supports RGB).
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Create an in-memory stream to hold the WEBP image.
    output_io = BytesIO()
    image.save(output_io, format="WEBP", quality=90)
    output_io.seek(0)

    # Create a new InMemoryUploadedFile for Django.
    webp_image = InMemoryUploadedFile(
        output_io,
        field_name=None,
        name=image_file.name.rsplit(".", 1)[0] + ".webp",
        content_type="image/webp",
        size=output_io.getbuffer().nbytes,
        charset=None,
    )
    return webp_image
