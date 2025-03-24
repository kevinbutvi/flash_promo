from rest_framework import viewsets, status, mixins, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from promotions.models import FlashPromo, PromoReservation
from promotions.serializers import (
    FlashPromoSerializer,
    PromoReservationSerializer,
    ExecutePromotionSerializer,
)
from django_celery_beat.models import PeriodicTask, ClockedSchedule
import json
from users.models import ClientProfile
from promotions.tasks import send_promo_notifications
from haversine import haversine
from utils.utils import redis_client


class FlashPromoViewSet(viewsets.ModelViewSet):
    queryset = FlashPromo.objects.all()
    serializer_class = FlashPromoSerializer
    permission_classes = [IsAdminUser]

    def perform_create(self, serializer):
        promo = serializer.save()
        if promo.is_active:
            if (
                promo.start_time.date() == timezone.now().date()
                and promo.start_time <= timezone.now()
            ):
                send_promo_notifications.delay(promo.id)
            else:

                schedule, _ = ClockedSchedule.objects.get_or_create(
                    clocked_time=promo.start_time
                )

                PeriodicTask.objects.create(
                    clocked=schedule,
                    name=f"Send promo notifications for promo {promo.id}",
                    task="send_promo_notifications",
                    kwargs=json.dumps({"promo_id": promo.id}),
                    one_off=True,
                )

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def execute_promotion(self, request):
        """Execute the listed promotions if are available to execute"""
        serializer = ExecutePromotionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        promos = serializer.validated_data["promo_ids"]

        for promo in promos:
            send_promo_notifications.delay(promo.id)

        return Response(
            {"message": f"Promotion notifications sended (Total={len(promos)})."},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def running(self, request):
        """Retuns running promotions"""
        now = timezone.now()
        active_promos = (
            FlashPromo.objects.filter(
                start_time__lte=now, end_time__gte=now, is_active=True
            )
            .select_related("product", "product__store")
            .prefetch_related("segments")
        )

        serializer = FlashPromoSerializer(active_promos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def eligible(self, request):
        """Returns the available promotions for the request user"""
        user_id = request.user.id
        try:
            user_profile = ClientProfile.objects.get(user_id=user_id)
        except ClientProfile.DoesNotExist:
            return Response([])

        now = timezone.now()
        active_promos = (
            FlashPromo.objects.filter(
                start_time__lte=now,
                end_time__gte=now,
                is_active=True,
                segments__in=user_profile.segments.all(),
            )
            .select_related("product", "product__store")
            .distinct()
        )

        # Filter by distance
        eligible_promos = []
        if user_profile.latitude is not None and user_profile.longitude is not None:
            user_location = (user_profile.latitude, user_profile.longitude)

            for promo in active_promos:
                store_location = (
                    promo.product.store.latitude,
                    promo.product.store.longitude,
                )
                distance = haversine(store_location, user_location)

                if distance <= float(promo.max_distance_km):
                    eligible_promos.append(promo)

        serializer = FlashPromoSerializer(eligible_promos, many=True)
        return Response(serializer.data)


class PromoReservationViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
):
    queryset = PromoReservation.objects.all()
    serializer_class = PromoReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PromoReservation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        promo = serializer.validated_data["promo"]
        now = timezone.now()

        if not (promo.is_active and promo.start_time <= now <= promo.end_time):
            raise serializers.ValidationError("This promotion is not active right now")

        reservation_key = f"reservation:{promo.id}:{self.request.user.id}"

        if redis_client.exists(reservation_key):
            raise serializers.ValidationError(
                "You allready have an active reservation for this product"
            )

        active_reservation_key = f"reservation:{promo.id}:*"
        if redis_client.keys(active_reservation_key):
            raise serializers.ValidationError(
                "This product was reserved for another user"
            )

        redis_client.set(reservation_key, self.request.user.id, ex=60)

        reservation = serializer.save(
            user=self.request.user, expires_at=now + timezone.timedelta(minutes=1)
        )
        return reservation

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None):
        """Complete a reservation (purchase completed)"""
        reservation = self.get_object()

        reservation_key = f"reservation:{reservation.promo.id}:{request.user.id}"
        if not redis_client.exists(reservation_key):
            return Response(
                {"error": "The reservation has expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if reservation.user != request.user:
            return Response(
                {"error": "This reservation belongs to another user"},
                status=status.HTTP_403_FORBIDDEN,
            )

        reservation.completed = True
        reservation.save()

        redis_client.delete(reservation_key)

        return Response({"status": "Purchase completed successfully"})
