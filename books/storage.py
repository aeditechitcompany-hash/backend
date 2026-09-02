import os
import uuid

from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from supabase import create_client, Client


@deconstructible
class SupabaseBookStorage(Storage):

    bucket_name = "books"

    def __init__(self):
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

        if not supabase_url:
            raise ValueError(
                "SUPABASE_URL environment variable is not set"
            )

        if not supabase_key:
            raise ValueError(
                "SUPABASE_SERVICE_ROLE_KEY environment variable is not set"
            )

        self.supabase: Client = create_client(
            supabase_url,
            supabase_key,
        )

    def _save(self, name, content):
        original_name = os.path.basename(
            name.replace("\\", "/")
        )

        # Give every uploaded PDF a unique filename.
        unique_name = f"{uuid.uuid4()}_{original_name}"

        file_data = content.read()

        self.supabase.storage.from_(
            self.bucket_name
        ).upload(
            path=unique_name,
            file=file_data,
            file_options={
                "content-type": "application/pdf",
                "cache-control": "3600",
                "upsert": "false",
            },
        )

        return unique_name

    def url(self, name):
        if not name:
            return ""

        supabase_url = os.environ.get("SUPABASE_URL")

        return (
            f"{supabase_url}/storage/v1/object/public/"
            f"{self.bucket_name}/{name}"
        )

    def delete(self, name):
        if not name:
            return

        self.supabase.storage.from_(
            self.bucket_name
        ).remove([name])

    def exists(self, name):
        return False