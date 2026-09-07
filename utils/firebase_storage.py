# Created by Atharva Mishra | 1/30/2026
# ACM MeteorMate | All Rights Reserved

from firebase_admin import storage
from google.cloud import exceptions

from utils.exceptions import Forbidden, NotFound


def delete_profile_picture(blob_path: str):
    """
    Function to delete a profile picture from firebase storage based on its blob path
    Args:
        blob_path (str): Path in firebase storage bucket to delete the image from
    Raises: HTTP Exceptions for either 404 or 403
    """
    try:
        bucket = storage.bucket()
        blob = bucket.blob(blob_path)

        if not blob.exists():
            raise NotFound("Profile picture")

        blob.delete()

    except exceptions.NotFound:
        raise NotFound("Storage bucket")

    except exceptions.Forbidden:
        raise Forbidden("Access to storage bucket denied")


def delete_all_profile_pictures(uid: str):
    """
    Function to delete all profile pictures of a user from firebase storage
    Args:
        user_id (str): User ID whose profile pictures are to be deleted
    Raises: HTTP Exceptions for either 404 or 403
    """
    try:
        bucket = storage.bucket()
        blobs = bucket.list_blobs(prefix=f"profile_pictures/{uid}/")

        for blob in blobs:
            blob.delete()

    except exceptions.NotFound:
        raise NotFound("Storage bucket")

    except exceptions.Forbidden:
        raise Forbidden("Access to storage bucket denied")
