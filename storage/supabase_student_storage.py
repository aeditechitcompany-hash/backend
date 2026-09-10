import os
import uuid

from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

from supabase import create_client, Client


@deconstructible
class SupabaseStudentStorage(Storage):

    bucket_name = "student-documents"

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
        name = name.replace("\\", "/")

        original_name = os.path.basename(name)

        unique_name = f"{uuid.uuid4()}_{original_name}"

        file_path = f"applications/{unique_name}"

        file_data = content.read()

        content_type = getattr(
            content,
            "content_type",
            None,
        ) or "application/octet-stream"

        print("========== SUPABASE UPLOAD ==========")
        print("Bucket:", self.bucket_name)
        print("Path:", file_path)
        print("Content type:", content_type)
        print("File size:", len(file_data))
        print("=====================================")

        try:
            response = (
                self.supabase
                .storage
                .from_(self.bucket_name)
                .upload(
                    path=file_path,
                    file=file_data,
                    file_options={
                        "content-type": content_type,
                        "cache-control": "3600",
                        "upsert": "false",
                    },
                )
            )

            print("========== SUPABASE RESPONSE ==========")
            print(response)
            print("=======================================")

        except Exception as e:
            print("========== SUPABASE UPLOAD ERROR ==========")
            print(type(e).__name__)
            print(str(e))
            print("============================================")
            raise

        return file_path

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

        try:
            self.supabase.storage.from_(
                self.bucket_name
            ).remove([name])
        except Exception as e:
            print("SUPABASE DELETE ERROR:", e)
            raise

    def exists(self, name):
        if not name:
            return False

        try:
            directory = os.path.dirname(name)
            filename = os.path.basename(name)

            response = (
                self.supabase
                .storage
                .from_(self.bucket_name)
                .list(directory or "")
            )

            return any(
                item.get("name") == filename
                for item in response
            )

        except Exception:
            return False