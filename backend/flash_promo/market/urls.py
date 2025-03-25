from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import StoreViewSet, ProductViewSet

router = DefaultRouter()
router.register(r"stores", StoreViewSet, basename="stores")
router.register(r"products", ProductViewSet, basename="products")

urlpatterns = [
    path("", include(router.urls)),
]
