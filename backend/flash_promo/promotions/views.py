from django.http import Http404
from rest_framework import viewsets, status, mixins, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from promotions.models import FlashPromo, PromoReservation
from promotions.serializers import (
    FlashPromoSerializer,
    PromoReservationSerializer,
)
from django.db import transaction
from django_celery_beat.models import PeriodicTask, ClockedSchedule
import json
from users.models import ClientProfile
from promotions.tasks import send_promo_notifications
from utils.utils import redis_client, filter_promos_by_distance


class FlashPromoViewSet(viewsets.ModelViewSet):
    queryset = FlashPromo.objects.all()
    serializer_class = FlashPromoSerializer
    permission_classes = [IsAdminUser]

    def _schedule_promo_notifications(self, promo):
        try:
            now = timezone.localtime()
            if not promo.is_active:
                return
            if promo.start_time.date() == now.date() and promo.start_time <= now:
                send_promo_notifications.delay(promo.id)
                return

            schedule, _ = ClockedSchedule.objects.get_or_create(
                clocked_time=promo.start_time
            )
            PeriodicTask.objects.create(
                clocked=schedule,
                name=f"Send promo notifications for promo {promo.id}",
                task="promotions.tasks.send_promo_notifications",
                kwargs=json.dumps({"promo_id": promo.id}),
                one_off=True,
            )
        except Exception:
            raise serializers.ValidationError(
                "There was an error scheduling notifications."
            )

    def perform_create(self, serializer):
        promo = serializer.save()
        self._schedule_promo_notifications(promo)

    def _get_running_promos(self, now=None):
        now = now or timezone.localtime()
        return (
            FlashPromo.objects.filter(
                start_time__lte=now, end_time__gte=now, is_active=True
            )
            .select_related("product", "product__store")
            .prefetch_related("segments")
        )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def running(self, request):
        """Returns running promotions"""
        active_promos = self._get_running_promos()

        page = self.paginate_queryset(active_promos)
        if page is not None:
            return self.get_paginated_response(
                FlashPromoSerializer(page, many=True).data
            )
        return Response(FlashPromoSerializer(active_promos, many=True).data)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def eligible(self, request):
        """Returns the available promotions for the user who requests"""
        user_id = request.user.id

        try:
            user_profile = ClientProfile.objects.get(user_id=user_id)
        except ClientProfile.DoesNotExist:
            return Response([])

        now = timezone.localtime()
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

        eligible_promos = filter_promos_by_distance(active_promos, user_profile)

        page = self.paginate_queryset(eligible_promos)
        if page is not None:
            return self.get_paginated_response(
                FlashPromoSerializer(page, many=True).data
            )

        return Response(FlashPromoSerializer(eligible_promos, many=True).data)


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

    def _validate_promo_active(self, promo):
        now = timezone.localtime()
        if not (promo.is_active and promo.start_time <= now <= promo.end_time):
            raise serializers.ValidationError(
                "This promotion is not active at the moment"
            )
        return now

    def _check_existing_reservations(self, reservation_key, active_reservation_key):
        if redis_client.exists(reservation_key):
            raise serializers.ValidationError(
                "You allready have an active reservation for this promotion"
            )

        if redis_client.keys(active_reservation_key):
            raise serializers.ValidationError(
                "This promotion was reserved for another user"
            )

    def perform_create(self, serializer):
        promo = serializer.validated_data["promo"]
        now = self._validate_promo_active(promo)

        user_profile = ClientProfile.objects.get(user=self.request.user)
        if not promo.segments.filter(id__in=user_profile.segments.all()).exists():
            raise serializers.ValidationError(
                "The requested promotion its not available for your user segment."
            )

        eligible_promos = filter_promos_by_distance([promo], user_profile)
        if not eligible_promos:
            raise serializers.ValidationError(
                "You cannot access this promotion because you are further away than the promotion allows."
            )
        reservation_key = f"reservation:{promo.id}:{user_profile.user.id}"
        active_reservation_key = f"reservation:{promo.id}:*"

        self._check_existing_reservations(reservation_key, active_reservation_key)

        try:
            redis_client.set(reservation_key, user_profile.user.id, ex=60)
            reservation = serializer.save(
                user=user_profile.user, expires_at=now + timezone.timedelta(minutes=1)
            )
            return reservation
        except Exception as e:
            redis_client.delete(reservation_key)
            raise serializers.ValidationError("Error creating the reservation")

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def complete(self, request, pk=None):
        """Complete a reservation (finish purchase)"""
        try:
            reservation = self.get_object()
            if reservation.user != request.user:
                return Response(
                    {"error": "This reservation belongs to another user"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            if reservation.completed:
                return Response(
                    {"error": "The reservation was successfully completed"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            reservation_key = f"reservation:{reservation.promo.id}:{request.user.id}"
            if not redis_client.exists(reservation_key):
                return Response(
                    {"error": "The reservation has expired"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            with transaction.atomic():
                reservation.completed = True
                reservation.save()
                reservation.promo.is_active = False
                reservation.promo.save()

            redis_client.delete(reservation_key)

            return Response({"status": "Purchase completed successfully"})

        except Http404:
            return Response(
                {"error": "Reservation not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"error": "Error processing reservation"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
