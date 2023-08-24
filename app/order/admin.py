from django.contrib.gis import admin

from .inlines import ProductInOrderInline
from .models import Cart, Order


@admin.register(Order)
class OrderAdmin(admin.OSMGeoAdmin):
    inlines = [ProductInOrderInline]
    list_display = ["user", "cost", "status", "dtype", "ptype"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    pass
