from rest_framework import viewsets
from .models import Country, City
from .serializers import CountrySerializer, CitySerializer


class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    filterset_fields = ["is_active"]
    search_fields = ["name", "code"]


class CityViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    filterset_fields = ["country", "is_active"]
    search_fields = ["name"]
