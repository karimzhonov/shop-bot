from django.contrib.gis.db import models


class Address(models.Model):
    name = models.CharField(max_length=255, unique=True)
    point = models.PointField()

    def __str__(self) -> str:
        return self.name