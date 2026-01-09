from django.contrib import admin
from django.utils.html import format_html
from .models import HeroSlide
from .models import HomeVideo




@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    ordering = ("order",)

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px; width:auto; border-radius:4px;" />',
                obj.image.url
            )
        return "-"

    preview.short_description = "Image"

@admin.register(HomeVideo)
class HomeVideoAdmin(admin.ModelAdmin):
    list_display = ("title", "is_active", "created_at")
    list_filter = ("is_active",)

