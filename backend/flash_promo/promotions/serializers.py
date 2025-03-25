from rest_framework import serializers
from promotions.models import FlashPromo, PromoReservation, PromoNotification
from market.serializers import ProductSerializer
from market.models import Product
from users.models import UserSegment
from users.serializers import UserSegmentSerializer
from django.utils import timezone


class FlashPromoSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True, source="product"
    )
    segments = UserSegmentSerializer(many=True, read_only=True)
    segment_ids = serializers.PrimaryKeyRelatedField(
        queryset=UserSegment.objects.all(),
        write_only=True,
        source="segments",
        many=True,
    )

    class Meta:
        model = FlashPromo
        fields = [
            "id",
            "product",
            "product_id",
            "promo_price",
            "start_time",
            "end_time",
            "segments",
            "segment_ids",
            "max_distance_km",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if end_time and end_time <= start_time:
            raise serializers.ValidationError(
                "End time must be greater than start time"
            )
        return data

    def create(self, validated_data):
        segments = validated_data.pop("segments")
        promo = FlashPromo.objects.create(**validated_data)
        promo.segments.set(segments)
        return promo

    def update(self, instance, validated_data):
        if "segments" in validated_data:
            segments = validated_data.pop("segments")
            instance.segments.set(segments)
        return super().update(instance, validated_data)


class PromoReservationSerializer(serializers.ModelSerializer):
    promo = FlashPromoSerializer(read_only=True)
    promo_id = serializers.PrimaryKeyRelatedField(
        queryset=FlashPromo.objects.all(), write_only=True, source="promo"
    )

    class Meta:
        model = PromoReservation
        fields = [
            "id",
            "promo",
            "promo_id",
            "reservation_id",
            "created_at",
            "expires_at",
            "completed",
        ]
        read_only_fields = ["reservation_id", "created_at", "expires_at", "completed"]


class PromoNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromoNotification
        fields = ["id", "promo", "user", "sent_at"]
        read_only_fields = ["sent_at"]


class ExecutePromotionSerializer(serializers.Serializer):
    promo_ids = serializers.PrimaryKeyRelatedField(
        queryset=FlashPromo.objects.all(),
        many=True,
        help_text="ID list of promotions to execute.",
    )

    def validate_promo_ids(self, value):
        now = timezone.localtime()
        invalid_promos = []

        for promo in value:
            if promo.end_time <= now or not promo.is_active:
                invalid_promos.append(promo.id)

        if invalid_promos:
            raise serializers.ValidationError(
                f"The following promotions are not valid because are deactivated or have already occurred: {invalid_promos}"
            )

        return value
