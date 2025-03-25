from django.contrib import admin
from .models import Store, Product


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ("name", "latitude", "longitude")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "store", "regular_price")
    search_fields = ("name", "store__name")
    list_filter = ("store",)
