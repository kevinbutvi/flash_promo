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
    # permission_classes = [IsAuthenticated]
