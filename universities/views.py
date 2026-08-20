from rest_framework import viewsets
from .models import University, Course
from .serializers import UniversitySerializer, CourseSerializer


class UniversityViewSet(viewsets.ModelViewSet):
    queryset = University.objects.select_related("country", "city").all()
    serializer_class = UniversitySerializer
    filterset_fields = ["country", "is_partner", "is_active"]
    search_fields = ["name"]


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related("university").all()
    serializer_class = CourseSerializer
    filterset_fields = ["university", "degree_level", "is_active"]
    search_fields = ["name"]
