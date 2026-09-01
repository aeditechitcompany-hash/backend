import os

import cloudinary
import cloudinary.uploader
import cloudinary.utils

from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class CloudinaryAudioStorage(Storage):

    def __init__(self):
        cloudinary.config(
            cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
            api_key=os.environ.get("CLOUDINARY_API_KEY"),
            api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
            secure=True,
        )

    def _save(self, name, content):
        name = name.replace("\\", "/")

        folder = os.path.dirname(name)
        filename = os.path.basename(name)

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