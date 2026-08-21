import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Create the production admin user if it does not already exist"

    def handle(self, *args, **options):
        User = get_user_model()

        email = os.environ.get("ADMIN_EMAIL")
        password = os.environ.get("ADMIN_PASSWORD")
        username = os.environ.get("ADMIN_USERNAME")

        if not email or not password:
            self.stdout.write(
                self.style.ERROR(
                    "ADMIN_EMAIL and ADMIN_PASSWORD environment variables are required."
                )
            )
            return

        username = username or email

        user = User.objects.filter(email=email).first()

        if user:
            self.stdout.write(
                self.style.WARNING(
                    f"Admin user {email} already exists."
                )
            )

            # Make sure the existing user has admin permissions.
            user.is_staff = True
            user.is_superuser = True
            user.role = "admin"
            user.set_password(password)
            user.save(
                update_fields=[
                    "is_staff",
                    "is_superuser",
                    "role",
                    "password",
                ]
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Admin user {email} has been updated."
                )
            )
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Admin user {user.email} created successfully."
            )
        )