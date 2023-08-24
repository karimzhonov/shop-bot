from django.contrib.gis import admin

from .models import Order, Cart
from .inlines import ProductInOrderInline


@admin.register(Order)
class OrderAdmin(admin.OSMGeoAdmin):
    inlines = [ProductInOrderInline]
    list_display = ["user", "cost", "status", "dtype", "ptype"]


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    pass
