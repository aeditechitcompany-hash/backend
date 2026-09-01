import os

import cloudinary
import cloudinary.uploader
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class CloudinaryAudioStorage(Storage):
    """
    Custom Cloudinary storage for audio files.

    Cloudinary stores audio files using resource_type="video".
    """

    def _save(self, name, content):
        # Normalize Windows paths
        name = name.replace("\\", "/")

        # Get folder and filename
        folder = os.path.dirname(name)
        filename = os.path.basename(name)

        # Remove extension from public_id because Cloudinary
        # adds the format when generating the URL.
        public_id = os.path.splitext(filename)[0]

        # Upload to Cloudinary as a video resource.
        # Cloudinary uses the video resource type for audio files.
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

        # Return the Cloudinary public ID.
        return result["public_id"]

    def url(self, name):
        """
        Return the secure Cloudinary URL for the audio file.
        """
        return cloudinary.utils.cloudinary_url(
            name,
            resource_type="video",
            secure=True,
        )[0]

    def delete(self, name):
        """
        Delete the audio file from Cloudinary.
        """
        if not name:
            return

        cloudinary.uploader.destroy(
            name,
            resource_type="video",
            invalidate=True,
        )

    def exists(self, name):
        """
        We don't need local filesystem existence checks.
        """
        return False