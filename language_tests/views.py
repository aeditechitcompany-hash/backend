from rest_framework import viewsets
from .models import LanguageTest
from .serializers import LanguageTestSerializer


class LanguageTestViewSet(viewsets.ModelViewSet):
    queryset = LanguageTest.objects.select_related("student").all()
    serializer_class = LanguageTestSerializer
    filterset_fields = ["student", "test_type", "is_verified"]
