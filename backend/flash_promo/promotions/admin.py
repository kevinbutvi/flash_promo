from django.contrib import admin
from .models import FlashPromo, PromoReservation, PromoNotification


@admin.register(FlashPromo)
class FlashPromoAdmin(admin.ModelAdmin):
    list_display = ("product", "promo_price", "start_time", "end_time", "is_active")
    list_filter = ("is_active", "start_time", "end_time")
    search_fields = ("product__name",)


@admin.register(PromoReservation)
class PromoReservationAdmin(admin.ModelAdmin):
    list_display = ("promo", "user", "reservation_id", "expires_at", "completed")
    list_filter = ("completed", "expires_at")
    search_fields = ("user__username", "reservation_id")


@admin.register(PromoNotification)
class PromoNotificationAdmin(admin.ModelAdmin):
    list_display = ("promo", "user", "sent_at")
    list_filter = ("sent_at",)
    search_fields = ("user__username", "promo__product__name")
