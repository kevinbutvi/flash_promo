from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/promotions/", include("promotions.urls")),
    path("api/market/", include("market.urls")),
    path("api/users/", include("users.urls")),
]
