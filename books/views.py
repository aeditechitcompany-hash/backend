from rest_framework import viewsets
from .models import Book
from .serializers import BookSerializer
from accounts.permissions import HasMCQAccess, IsCounselor


class BookViewSet(viewsets.ModelViewSet):

    queryset = Book.objects.all()

    serializer_class = BookSerializer

    def get_permissions(self):

        if self.action in (
            "create",
            "update",
            "partial_update",
            "destroy",
        ):
            return [IsCounselor()]

        return [HasMCQAccess()]
