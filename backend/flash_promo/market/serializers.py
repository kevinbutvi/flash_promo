from rest_framework import serializers
from market.models import Store, Product


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ["id", "name", "latitude", "longitude"]


class ProductSerializer(serializers.ModelSerializer):
    store = StoreSerializer(read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "store", "regular_price"]
