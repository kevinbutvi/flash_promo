from rest_framework import serializers
from users.models import UserSegment, ClientProfile
from django.contrib.auth.models import User


class UserSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSegment
        fields = ["id", "name", "description"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class ClientProfileSerializer(serializers.ModelSerializer):
    segments = UserSegmentSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = ClientProfile
        fields = [
            "id",
            "user",
            "segments",
            "latitude",
            "longitude",
            "last_notification_date",
        ]
        read_only_fields = ["user", "last_notification_date"]
