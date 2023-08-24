from uuid import uuid4
from django.contrib.gis.db import models
from payment.models import PAYMENT_TYPES


ORDER_DELIVERY_TYPE = (
    ("delivery", "Доставка"),
    ("come", "Сам вызов"),
)

ORDER_STATUS = (
    ("accept", "Принята"),
    ("payed", "Оплачено"),
    ("finished", "Выполнена"),
)
    

class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    user = models.ForeignKey("bot.User", models.CASCADE)
    product = models.ForeignKey("product.Product", models.CASCADE)
    qty = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = (("user", "product"),)


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    user = models.ForeignKey("bot.User", models.CASCADE)
    point = models.PointField(blank=True, null=True)
    dtype = models.CharField(max_length=20, choices=ORDER_DELIVERY_TYPE)
    address = models.ForeignKey("address.Address", models.PROTECT, blank=True, null=True)
    status = models.CharField(max_length=20, default="accept", choices=ORDER_STATUS)
    ptype = models.CharField(max_length=255, choices=PAYMENT_TYPES)
    come_date = models.DateTimeField()
    pay_date = models.DateTimeField(blank=True, null=True)
    
    
    async def acost(self):
        agg = await self.productinorder_set.aaggregate(sum=models.Sum("cost"))
        return agg.get("sum", 0) or 0
    
    @property
    def cost(self):
        return self.productinorder_set.aggregate(sum=models.Sum("cost")).get("sum", 0) or 0


class ProductInOrder(models.Model):
    order = models.ForeignKey(Order, models.PROTECT)
    product = models.ForeignKey("product.Product", models.PROTECT)
    qty = models.PositiveIntegerField()
    cost = models.FloatField()
