from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Person
from .serializers import PersonSerializer


def ping(request):
    return JsonResponse({"message": "pong"})


class PersonViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar las operaciones CRUD del modelo Person.
    """

    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Permite filtrar las personas activas si es necesario.
        """
        queryset = super().get_queryset()
        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")
        return queryset
