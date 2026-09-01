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
class CloudinaryPDFStorage(Storage):
    """
    Storage for PDF files uploaded to Cloudinary.
    """

    def __init__(self):
        configure_cloudinary()

    def _save(self, name, content):
        name = name.replace("\\", "/")

        folder = os.path.dirname(name)

        options = {
            "resource_type": "raw",
            "use_filename": True,
            "unique_filename": True,
            "format": "pdf",
        }

        if folder:
            options["folder"] = folder

        result = cloudinary.uploader.upload(
            content,
            **options,
        )

        return result["public_id"]

    def url(self, name):
        configure_cloudinary()

        return cloudinary.utils.cloudinary_url(
            name,
            resource_type="raw",
            secure=True,
        )[0]

    def delete(self, name):
        if name:
            configure_cloudinary()

            cloudinary.uploader.destroy(
                name,
                resource_type="raw",
                invalidate=True,
            )

    def exists(self, name):
        return False