from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
import csv

from .models import Order, OrderItem


# =========================
# INLINE ORDER ITEMS
# =========================
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "quantity", "price")
    can_delete = False


# =========================
# ADMIN ACTIONS
# =========================
@admin.action(description="Mark selected orders as Shipped")
def mark_as_shipped(modeladmin, request, queryset):
    queryset.update(status="shipped")


@admin.action(description="Mark selected orders as Delivered")
def mark_as_delivered(modeladmin, request, queryset):
    queryset.update(status="delivered")


@admin.action(description="Export selected orders to CSV")
def export_orders_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="orders.csv"'

    writer = csv.writer(response)
    writer.writerow(["Order ID", "User", "Status", "Total Amount", "Created At"])

    for order in queryset:
        writer.writerow([
            order.order_id,
            order.user.username if order.user else "",
            order.status,
            order.total_amount,
            order.created_at,
        ])

    return response


# =========================
# ORDER ADMIN
# =========================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_id",
        "user",
        "colored_status",
        "total_amount",
        "created_at",
        "download_invoice",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "order_id",
        "user__username",
        "user__email",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "order_id",
        "user",
        "total_amount",
        "created_at",
        "order_timeline",
    )

    inlines = [OrderItemInline]

    actions = [
        mark_as_shipped,
        mark_as_delivered,
        export_orders_csv,
    ]

    fieldsets = (
        ("Order Info", {
            "fields": ("order_id", "user", "status", "order_timeline")
        }),
        ("Payment", {
            "fields": ("total_amount",)
        }),
        ("Dates", {
            "fields": ("created_at",)
        }),
    )

    def has_add_permission(self, request):
        return False  # ❌ Orders should NOT be created from admin

    def has_delete_permission(self, request, obj=None):
        return False  # ❌ Prevent accidental deletion


    # =========================
    # STATUS BADGE
    # =========================
    def colored_status(self, obj):
        color_map = {
            "pending": "#facc15",     # yellow
            "shipped": "#3b82f6",     # blue
            "delivered": "#22c55e",   # green
            "cancelled": "#ef4444",   # red
        }

        color = color_map.get(obj.status, "#6b7280")

        return format_html(
            '<span style="padding:4px 10px; border-radius:12px; '
            'background:{}; color:black; font-weight:600;">{}</span>',
            color,
            obj.status.capitalize()
        )

    colored_status.short_description = "Status"


    # =========================
    # ORDER TIMELINE
    # =========================
    def order_timeline(self, obj):
        steps = ["pending", "shipped", "delivered"]
        html = ""

        for step in steps:
            if step == obj.status:
                html += f"<b>{step.capitalize()}</b> → "
            else:
                html += f"{step.capitalize()} → "

        return format_html(html.rstrip(" → "))

    order_timeline.short_description = "Order Progress"


    # =========================
    # INVOICE LINK (PLACEHOLDER)
    # =========================
    def download_invoice(self, obj):
        return format_html(
            '<a href="/admin/orders/order/{}/invoice/" '
            'style="font-weight:600;">Download</a>',
            obj.id
        )

    download_invoice.short_description = "Invoice"
