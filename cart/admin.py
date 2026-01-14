from django.contrib import admin
from .models import Coupon

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "discount_percent", "active", "expiry_date")
    list_filter = ("active", "expiry_date")
    search_fields = ("code",)