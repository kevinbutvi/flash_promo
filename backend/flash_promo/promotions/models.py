from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
from utils.models import BaseModel
from users.models import UserSegment
from market.models import Product


class FlashPromo(BaseModel):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="flash_promos"
    )
    promo_price = models.DecimalField(max_digits=10, decimal_places=2)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    segments = models.ManyToManyField(UserSegment, related_name="targeted_promos")
    max_distance_km = models.DecimalField(max_digits=4, decimal_places=2, default=2.0)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} - {self.promo_price}"

    def is_valid_now(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time and self.is_active

    class Meta:
        indexes = [
            models.Index(fields=["start_time", "end_time", "is_active"]),
        ]


class PromoReservation(BaseModel):
    promo = models.ForeignKey(
        FlashPromo, on_delete=models.CASCADE, related_name="reservations"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="promo_reservations"
    )
    reservation_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    expires_at = models.DateTimeField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Reservation {self.reservation_id} for {self.user.username}"

    def is_expired(self):
        now = timezone.now()
        return now > self.expires_at

    def reserve(self, minutes=1):
        self.expires_at = timezone.now() + timezone.timedelta(minutes=minutes)
        self.save()
        return self.reservation_id

    def complete(self):
        self.completed = True
        self.save()


class PromoNotification(BaseModel):
    promo = models.ForeignKey(
        FlashPromo, on_delete=models.CASCADE, related_name="notifications"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="promo_notifications"
    )
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("promo", "user")

    def __str__(self):
        return f"Notification to {self.user.username} for {self.promo.product.name}"
