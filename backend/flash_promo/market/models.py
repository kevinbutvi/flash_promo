from django.db import models
from utils.models import BaseModel


class Store(BaseModel):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.name


class Product(BaseModel):
    name = models.CharField(max_length=100)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name="products")
    regular_prince = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name(self.store)
