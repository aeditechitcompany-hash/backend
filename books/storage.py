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

    def __init__(self):
        configure_cloudinary()

    def _save(self, name, content):
        name = name.replace("\\", "/")

        folder = os.path.dirname(name)
        filename = os.path.basename(name)

        # Remove .pdf from the public ID.
        # Image/video Cloudinary public IDs should not contain
        # the file extension.
        public_id = os.path.splitext(filename)[0]

        options = {
            "resource_type": "image",
            "use_filename": True,
            "unique_filename": True,
            "public_id": public_id,
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
            resource_type="image",
            format="pdf",
            secure=True,
        )[0]

    def delete(self, name):
        if name:
            configure_cloudinary()

            cloudinary.uploader.destroy(
                name,
                resource_type="image",
                invalidate=True,
            )

    def exists(self, name):
        return False