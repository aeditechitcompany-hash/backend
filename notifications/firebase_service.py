import os

import firebase_admin
from firebase_admin import credentials, messaging


def _initialize_firebase():
    if firebase_admin._apps:
        return

    private_key = os.getenv("FIREBASE_PRIVATE_KEY")

    if private_key:
        private_key = private_key.replace("\\n", "\n")

    service_account = {
        "type": os.getenv("FIREBASE_TYPE", "service_account"),
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": private_key,
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
        "auth_uri": os.getenv(
            "FIREBASE_AUTH_URI",
            "https://accounts.google.com/o/oauth2/auth",
        ),
        "token_uri": os.getenv(
            "FIREBASE_TOKEN_URI",
            "https://oauth2.googleapis.com/token",
        ),
        "auth_provider_x509_cert_url": os.getenv(
            "FIREBASE_AUTH_PROVIDER_X509_CERT_URL",
            "https://www.googleapis.com/oauth2/v1/certs",
        ),
        "client_x509_cert_url": os.getenv(
            "FIREBASE_CLIENT_X509_CERT_URL",
        ),
        "universe_domain": os.getenv(
            "FIREBASE_UNIVERSE_DOMAIN",
            "googleapis.com",
        ),
    }

    required = [
        "project_id",
        "private_key",
        "client_email",
    ]

    if not all(service_account.get(key) for key in required):
        raise RuntimeError(
            "Firebase environment variables are not configured."
        )

    cred = credentials.Certificate(service_account)

    firebase_admin.initialize_app(cred)


def send_push_notification(
    token: str,
    title: str,
    body: str,
    data: dict | None = None,
):
    _initialize_firebase()

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data={
            str(key): str(value)
            for key, value in (data or {}).items()
        },
        token=token,
    )

    try:
        return messaging.send(message)
    except Exception as exc:
        print(f"Firebase push notification failed: {exc}")
        return None