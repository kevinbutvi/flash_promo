from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientProfileViewSet, UserSegmentViewSet

router = DefaultRouter()
router.register(r"user-segments", UserSegmentViewSet, basename="user-segments")
router.register(r"clients-profiles", ClientProfileViewSet, basename="client-profiles")

urlpatterns = [
    path("", include(router.urls)),
]
