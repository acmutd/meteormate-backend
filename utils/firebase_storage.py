import base64
import binascii
import io
from fastapi import HTTPException
from firebase_admin import storage
from google.cloud.exceptions import NotFound, Forbidden
from PIL import Image, ImageOps


def convert_to_webp_bytes(image_bytes: bytes) -> bytes:
    img = Image.open(io.BytesIO(image_bytes))

    # Fix orientation (EXIF)
    img = ImageOps.exif_transpose(img)

    # Normalize color mode
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


def upload_profile_picture(data: str, blob_path: str) -> str:
    '''
    Function to upload a profile pic based on its base64 data
    Returns: public download url to that image
    Raises: HTTP Exceptions for either 422, 404, or 403
    '''
    try:
        image_bytes = base64.b64decode(data)
        image_bytes = convert_to_webp_bytes(image_bytes)

        bucket = storage.bucket()
        blob = bucket.blob(blob_path)

        blob.upload_from_string(image_bytes, content_type=f"image/webp")

        blob.make_public()

        return blob.public_url

    except binascii.Error as e:
        raise HTTPException(
            status_code=422,  # unprocessable entity
            detail="image data has incorrect padding or invalid characters",
        )

    except NotFound:
        raise HTTPException(
            status_code=404,  # not found
            detail="blob or bucket not found",
        )

    except Forbidden:
        raise HTTPException(
            status_code=403,  # forbidden
            detail="forbidden request, no authorization to access bucket",
        )
