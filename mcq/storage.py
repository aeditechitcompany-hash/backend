import os

import cloudinary
import cloudinary.uploader
import cloudinary.utils

from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


def configure_cloudinary():
    cloudinary.config(
        cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
        api_key=os.environ.get("CLOUDINARY_API_KEY"),
        api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
        secure=True,
    )


@deconstructible
class CloudinaryMediaStorage(Storage):
    """
    Storage for images uploaded to Cloudinary.
    """

    def __init__(self):
        configure_cloudinary()

    def _save(self, name, content):
        name = name.replace("\\", "/")

        folder = os.path.dirname(name)

        options = {
            "resource_type": "image",
            "use_filename": True,
            "unique_filename": True,
        }

        if folder:
            options["folder"] = folder

        result = cloudinary.uploader.upload(
            content,
            **options,
        )

        return result["public_id"]

    def url(self, name):
        return cloudinary.utils.cloudinary_url(
            name,
            resource_type="image",
            secure=True,
        )[0]

    def delete(self, name):
        if name:
            cloudinary.uploader.destroy(
                name,
                resource_type="image",
                invalidate=True,
            )

    def exists(self, name):
        return False


@deconstructible
class CloudinaryAudioStorage(Storage):
    """
    Storage for audio files uploaded to Cloudinary.

    Cloudinary uses resource_type="video" for audio files.
    """

    def __init__(self):
        configure_cloudinary()

    def _save(self, name, content):
        name = name.replace("\\", "/")

        folder = os.path.dirname(name)

        options = {
            "resource_type": "video",
            "use_filename": True,
            "unique_filename": True,
        }

        if folder:
            options["folder"] = folder

        result = cloudinary.uploader.upload(
            content,
            **options,
        )

        return result["public_id"]

    def url(self, name):
        return cloudinary.utils.cloudinary_url(
            name,
            resource_type="video",
            secure=True,
        )[0]

    def delete(self, name):
        if name:
            cloudinary.uploader.destroy(
                name,
                resource_type="video",
                invalidate=True,
            )

    def exists(self, name):
        return False