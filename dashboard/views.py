from rest_framework.views import APIView
from rest_framework.response import Response

from students.models import StudentProfile
from applications.models import Application
from visas.models import VisaApplication
from universities.models import University
from interviews.models import Interview
from documents.models import Document


class DashboardSummaryView(APIView):
    def get(self, request):
        data = {
            "total_students": StudentProfile.objects.count(),
            "total_universities": University.objects.count(),
            "applications": {
                "total": Application.objects.count(),
                "draft": Application.objects.filter(status=Application.Status.DRAFT).count(),
                "submitted": Application.objects.filter(status=Application.Status.SUBMITTED).count(),
                "offer_received": Application.objects.filter(status=Application.Status.OFFER_RECEIVED).count(),
                "accepted": Application.objects.filter(status=Application.Status.ACCEPTED).count(),
                "rejected": Application.objects.filter(status=Application.Status.REJECTED).count(),
            },
            "visas": {
                "total": VisaApplication.objects.count(),
                "approved": VisaApplication.objects.filter(status=VisaApplication.Status.APPROVED).count(),
                "rejected": VisaApplication.objects.filter(status=VisaApplication.Status.REJECTED).count(),
            },
            "interviews": {
                "upcoming": Interview.objects.filter(status=Interview.Status.SCHEDULED).count(),
                "completed": Interview.objects.filter(status=Interview.Status.COMPLETED).count(),
            },
            "documents": {
                "pending_review": Document.objects.filter(status=Document.Status.PENDING).count(),
            },
        }
        return Response(data)
