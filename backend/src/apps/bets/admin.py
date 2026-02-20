# Register your models here.

from django.contrib import admin

from .infrastructure.models.bet_category_model import BetCategoryModel
from .infrastructure.models.bet_status_model import BetStatusModel
from .infrastructure.models.sport_model import SportModel


@admin.register(SportModel)
class SportAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)


@admin.register(BetStatusModel)
class BetStatusAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "is_final")
    search_fields = ("name", "code")


@admin.register(BetCategoryModel)
class BetCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)
