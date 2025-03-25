from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FlashPromoViewSet, PromoReservationViewSet

router = DefaultRouter()
router.register(r"flash-promos", FlashPromoViewSet, basename="flash-promos")
router.register(
    r"promo-reservations", PromoReservationViewSet, basename="promo-reservations"
)

urlpatterns = [
    path("", include(router.urls)),
]
