from django.contrib import admin

from .models import User, FAQ


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    pass
