from django.urls import path
from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PersonViewSet

router = DefaultRouter()
router.register(r"persons", PersonViewSet, basename="person")


urlpatterns = [
    path("", include(router.urls)),
    path("ping/", views.ping, name="ping"),
]
