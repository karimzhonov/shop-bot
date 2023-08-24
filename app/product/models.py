from django.db import models

# from parler.models import TranslatableModel, TranslatedFields


class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey("self", models.CASCADE, blank=True, null=True)


    def __str__(self) -> str:
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    desc = models.TextField(default="")
    photo = models.ImageField(upload_to="product")
    price = models.FloatField()
    category = models.ForeignKey(Category, models.CASCADE)

    def __str__(self) -> str:
        return self.name
