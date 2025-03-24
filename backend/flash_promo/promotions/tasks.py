from celery import shared_task
from django.utils import timezone
from django.db import transaction
from users.models import ClientProfile
from promotions.models import FlashPromo, PromoNotification
from utils.utils import (
    get_eligible_users_for_promo,
    filter_users_by_distance,
    notificate_user,
)
from cacheops import invalidate_model


@shared_task
def send_promo_notifications(promo_id):
    try:
        promo = (
            FlashPromo.objects.select_related("product", "product__store")
            .prefetch_related("segments")
            .get(id=promo_id)
        )

        store_location = (promo.product.store.latitude, promo.product.store.longitude)
        max_distance = float(promo.max_distance_km)

        eligible_users = get_eligible_users_for_promo(promo)

        nearby_users = filter_users_by_distance(
            eligible_users, store_location, max_distance
        )

        notifications_to_create = []
        users_to_update = []

        for user_profile in nearby_users:
            notifications_to_create.append(
                PromoNotification(promo=promo, user=user_profile.user)
            )
            user_profile.last_notification_date = timezone.now()
            users_to_update.append(user_profile)
            notificate_user(user_profile.user, promo)

        with transaction.atomic():
            if notifications_to_create:
                PromoNotification.objects.bulk_create(
                    notifications_to_create,
                    ignore_conflicts=True,
                )
                invalidate_model(PromoNotification)

            if users_to_update:
                ClientProfile.objects.bulk_update(
                    users_to_update, ["last_notification_date"]
                )
                invalidate_model(ClientProfile)

        return {"status": "success", "notified_users": len(notifications_to_create)}

    except FlashPromo.DoesNotExist:
        return {"status": "error", "message": "Promo not found"}
