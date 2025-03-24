from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import viewsets
from users.models import ClientProfile, UserSegment
from users.serializers import (
    ClientProfileSerializer,
    UserSegmentSerializer,
)


class UserSegmentViewSet(viewsets.ModelViewSet):
    queryset = UserSegment.objects.all()
    serializer_class = UserSegmentSerializer
    permission_classes = [IsAdminUser]


class ClientProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ClientProfile.objects.all()
    serializer_class = ClientProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if not self.request.user.is_staff:
            return ClientProfile.objects.filter(user=self.request.user)
        return ClientProfile.objects.all()
