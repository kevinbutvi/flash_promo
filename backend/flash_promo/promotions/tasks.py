from celery import shared_task
from django.utils import timezone
from django.db import transaction
from django.db.models import Q
from users.models import ClientProfile
from promotions.models import FlashPromo, PromoNotification
from haversine import haversine


@shared_task(name="send_promo_notifications")
def send_promo_notifications(promo_id):
    """Envía notificaciones simbólicas a usuarios elegibles para una promoción específica"""
    try:

        promo = FlashPromo.objects.select_related("product", "product__store").get(
            id=promo_id
        )
        today = timezone.now().date()

        # Obtener segmentos de usuarios para esta promoción
        segment_ids = promo.segments.values_list("id", flat=True)

        # Obtener usuarios elegibles por segmento que no han recibido notificaciones hoy
        eligible_users = (
            ClientProfile.objects.filter(
                Q(last_notification_date__isnull=True)
                | Q(last_notification_date__date__lt=today),
                segments__id__in=segment_ids,
            )
            .select_related("user")
            .distinct()
        )

        store_location = (promo.product.store.latitude, promo.product.store.longitude)
        max_distance = float(promo.max_distance_km)

        # Procesar usuarios en lotes para evitar problemas de memoria
        batch_size = 1000
        total_notified = 0
        # TODO improve this
        for i in range(0, eligible_users.count(), batch_size):
            batch_users = eligible_users[i : i + batch_size]
            notifications_to_create = []
            users_to_update = []

            for user_profile in batch_users:
                # Verificar ubicación
                if user_profile.latitude and user_profile.longitude:
                    user_location = (user_profile.latitude, user_profile.longitude)
                    distance = haversine(store_location, user_location)

                    if distance <= max_distance:
                        # Crear notificación
                        notifications_to_create.append(
                            PromoNotification(promo=promo, user=user_profile.user)
                        )

                        # Actualizar fecha de última notificación
                        user_profile.last_notification_date = timezone.now()
                        users_to_update.append(user_profile)

                        # Notificación simbólica (print)
                        notification_data = {
                            "type": "flash_promo",
                            "promo_id": promo.id,
                            "product_name": promo.product.name,
                            "store_name": promo.product.store.name,
                            "notificated_user": user_profile.user.username,
                            "end_time": promo.end_time.isoformat(),
                        }
                        print(f"Notificación enviada: {notification_data}")

            # Guardar notificaciones y actualizar perfiles en lotes
            with transaction.atomic():
                if notifications_to_create:
                    PromoNotification.objects.bulk_create(
                        notifications_to_create,
                        ignore_conflicts=True,  # Ignorar duplicados
                    )

                for profile in users_to_update:
                    profile.save(update_fields=["last_notification_date"])

            total_notified += len(notifications_to_create)

        return {"status": "success", "notified_users": total_notified}

    except FlashPromo.DoesNotExist:
        return {"status": "error", "message": "Promo not found"}
