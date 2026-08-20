from rest_framework import serializers
from .models import LanguageTest


class LanguageTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = LanguageTest
        fields = "__all__"
