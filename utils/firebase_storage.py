import io
from firebase_admin import storage
from google.cloud import exceptions
from PIL import Image, ImageOps, UnidentifiedImageError

from exceptions import Forbidden, NotFound, UnprocessableEntity

# function normalizes color type for the image and converts image bytes to webp bytes 
def process_image(image_bytes: bytes) -> bytes:
    try:
        with Image.open(io.BytesIO(image_bytes)) as img:
            img = ImageOps.exif_transpose(img)

            if img.mode != "RGB":
                img = img.convert("RGB")

            buffer = io.BytesIO()
            img.save(
                buffer,
                format="WEBP",
                quality=80,
                method=6,
                optimize=True,
            )

            return buffer.getvalue()

    except UnidentifiedImageError:
        raise UnprocessableEntity("Uploaded file is not a valid image")

    except (OSError, ValueError, RuntimeError) as e:
        raise UnprocessableEntity(
            "Failed to process image; the file may be corrupted or unsupported"
        )

    except MemoryError:
        raise UnprocessableEntity("Image is too large to process")


def upload_profile_picture(data: bytes, blob_path: str) -> str:
    """
    Function to upload a profile pic based on its base64 data
    Returns: public download url to that image
    Raises: HTTP Exceptions for either 422, 404, or 403
    """
    try:
        image_bytes = process_image(data)

        bucket = storage.bucket()
        blob = bucket.blob(blob_path)

        blob.upload_from_string(image_bytes, content_type=f"image/webp")

        blob.make_public()

        return blob.public_url

    except exceptions.NotFound:
        raise NotFound("Storage bucket")

    except exceptions.Forbidden:
        raise Forbidden("Access to storage bucket denied")
