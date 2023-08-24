from django.db import models


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.SlugField(blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)

    is_admin = models.BooleanField(default=False)


class FAQ(models.Model):
    user = models.ForeignKey(User, models.CASCADE)
    question = models.TextField()
    is_active = models.BooleanField(default=True)
    