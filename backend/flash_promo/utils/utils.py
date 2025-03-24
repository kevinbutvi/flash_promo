from django.conf import settings
import redis
from django.utils import timezone
from django.db.models import Q
from users.models import ClientProfile
from haversine import haversine
import logging

redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=2, decode_responses=True
)

logger = logging.getLogger(__name__)


def get_eligible_users_for_promo(promo):
    today = timezone.now().date()
    segment_ids = promo.segments.values_list("id", flat=True)

    eligible_users = (
        ClientProfile.objects.filter(
            Q(last_notification_date__isnull=True)
            | Q(last_notification_date__date__lt=today),
            segments__id__in=segment_ids,
            latitude__isnull=False,
            longitude__isnull=False,
        )
        .select_related("user")
        .distinct()
    )

    return eligible_users


def filter_users_by_distance(users, store_location, max_distance):
    nearby_users = []
    for user_profile in users:
        user_location = (user_profile.latitude, user_profile.longitude)
        distance = haversine(store_location, user_location)

        if distance <= max_distance:
            nearby_users.append(user_profile)

    return nearby_users


def notificate_user(user_profile, promo):
    logger.info(
        "Promo Notification",
        extra={
            "promo_id": promo.id,
            "product_name": promo.product.name,
            "store_name": promo.product.store.name,
            "notified_user": user_profile.username,
            "end_time": promo.end_time.isoformat(),
        },
    )


def filter_promos_by_distance(promos, user_profile):

    if not user_profile.latitude or not user_profile.longitude:
        return []

    user_location = (user_profile.latitude, user_profile.longitude)
    eligible_promos = []

    for promo in promos:
        store_location = (
            promo.product.store.latitude,
            promo.product.store.longitude,
        )
        distance = haversine(store_location, user_location)

        if distance <= float(promo.max_distance_km):
            eligible_promos.append(promo)

    return eligible_promos
