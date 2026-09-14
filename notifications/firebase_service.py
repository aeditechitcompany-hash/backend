from firebase_admin import messaging

from firebase_admin import credentials, messaging
from django.conf import settings

from .models import DeviceToken

# Initialize Firebase Admin SDK only once
if not firebase_admin._apps:
    cred = credentials.Certificate(
        settings.FIREBASE_SERVICE_ACCOUNT_FILE
    )
    firebase_admin.initialize_app(cred)

    
def send_push_notification(
    *,
    user,
    title,
    message,
):
    """
    Send an FCM push notification to all active devices
    registered for this user.
    """

    device_tokens = DeviceToken.objects.filter(
        user=user,
        is_active=True,
    )

    for device_token in device_tokens:
        try:
            fcm_message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=message,
                ),
                token=device_token.token,
            )

            response = messaging.send(fcm_message)

            print(
                f"FCM notification sent to {user.email}: "
                f"{response}"
            )

        except Exception as e:
            print(
                f"FCM notification failed for "
                f"{user.email}: {e}"
            )