from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from market.models import Store, Product
from market.serializers import StoreSerializer, ProductSerializer


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        if self.request.method in ["GET"]:
            return Store.objects.all()
        return super().get_queryset()


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        if self.request.method in ["GET"]:
            return Product.objects.all()
        return super().get_queryset()
