
from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings


def delete_account_request(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        reason = request.POST.get("reason", "").strip()

        if not email or not phone:
            messages.error(
                request,
                "Please provide your registered email and phone number."
            )
        else:
            try:
                send_mail(
                    subject="Account Deletion Request - Nibangsh Consultancy",
                    message=(
                        f"Email: {email}\n"
                        f"Phone: {phone}\n"
                        f"Reason: {reason}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=["info@nibangshconsultancy.com"],
                    fail_silently=False,
                )

                messages.success(
                    request,
                    "Your deletion request has been submitted. "
                    "Our team will contact you after verification."
                )

            except Exception:
                messages.error(
                    request,
                    "Unable to submit your request. Please email "
                    "info@nibangshconsultancy.com directly."
                )

    return render(request, "accounts/delete_account.html")
