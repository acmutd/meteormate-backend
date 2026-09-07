# Created by Atharva Mishra | 1/30/2026
# ACM MeteorMate | All Rights Reserved

import logging

from firebase_admin import storage
from google.cloud import exceptions

from utils.exceptions import AppException, Forbidden, InternalServerError, NotFound


logger = logging.getLogger("meteormate." + __name__)


def delete_profile_picture(blob_path: str):
    """
    Function to delete a profile picture from firebase storage based on its blob path
    Args:
        blob_path (str): Path in firebase storage bucket to delete the image from
    Raises: HTTP Exceptions for either 404 or 403
    """
    bucket_name = "unknown"

    try:
        bucket = storage.bucket()
        bucket_name = bucket.name
        blob = bucket.blob(blob_path)

        logger.info(
            "Checking profile picture before delete (bucket=%s, blob_path=%s)",
            bucket_name,
            blob_path,
        )

        if not blob.exists():
            logger.warning(
                "Profile picture does not exist (bucket=%s, blob_path=%s)",
                bucket_name,
                blob_path,
            )
            raise NotFound("Profile picture")

        blob.delete()
        logger.info(
            "Deleted profile picture (bucket=%s, blob_path=%s)",
            bucket_name,
            blob_path,
        )

    except exceptions.NotFound as exc:
        logger.warning(
            "Firebase Storage returned NotFound (bucket=%s, blob_path=%s): %s",
            bucket_name,
            blob_path,
            exc,
        )
        raise NotFound("Storage bucket")

    except exceptions.Forbidden as exc:
        logger.error(
            "Firebase Storage denied profile picture deletion "
            "(bucket=%s, blob_path=%s): %s",
            bucket_name,
            blob_path,
            exc,
        )
        raise Forbidden("Access to storage bucket denied")

    except AppException:
        # Expected application errors are already logged above.
        raise

    except Exception as exc:
        logger.exception(
            "Unexpected Firebase Storage error while deleting profile picture "
            "(bucket=%s, blob_path=%s, exception_type=%s)",
            bucket_name,
            blob_path,
            type(exc).__name__,
        )
        raise InternalServerError("Failed to delete profile picture") from exc


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
