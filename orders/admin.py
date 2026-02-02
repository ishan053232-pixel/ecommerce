from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
import csv
from orders.utils.invoice import generate_invoice
from django.core.mail import EmailMessage
from .models import (
    Order,
    OrderItem,
    PendingOrder,
    ProcessingOrder,
    ShippedOrder,
    DeliveredOrder,
    CancelledOrder,
)

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
    for order in queryset:
        order.status = "delivered"
        order.save()

        # 🔥 Generate invoice here
        generate_invoice(order)


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
# BASE ORDER ADMIN (REUSED)
# =========================
class BaseOrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_id",
        "user",
        "colored_status",
        "total_amount",
        "created_at",
    )

    list_select_related = ("user",)
    search_fields = ("order_id", "user__username", "user__email")
    ordering = ("-created_at",)
    readonly_fields = ("order_id", "user", "total_amount", "created_at")
    inlines = [OrderItemInline]

    actions = [mark_as_shipped, mark_as_delivered, export_orders_csv]

    def has_add_permission(self, request):
        return False  # Orders created via checkout only

    def has_delete_permission(self, request, obj=None):
        return False  # Prevent deletion

    # ===== STATUS BADGE =====
    def colored_status(self, obj):
        colors = {
            "pending": "#facc15",
            "processing": "#60a5fa",
            "shipped": "#a78bfa",
            "delivered": "#22c55e",
            "cancelled": "#ef4444",
        }

        return format_html(
            '<span style="padding:4px 10px;border-radius:12px;'
            'background:{};color:black;font-weight:600;">{}</span>',
            colors.get(obj.status, "#9ca3af"),
            obj.get_status_display(),
        )

    colored_status.short_description = "Status"


# =========================
# ALL ORDERS (MIXED VIEW)
# =========================
@admin.register(Order)
class OrderAdmin(BaseOrderAdmin):
    list_filter = ("status", "created_at")
    readonly_fields = BaseOrderAdmin.readonly_fields + ("order_timeline",)

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

    def order_timeline(self, obj):
        steps = ["pending", "processing", "shipped", "delivered"]
        return " → ".join(
            f"[{step.upper()}]" if step == obj.status else step.capitalize()
            for step in steps
        )

    order_timeline.short_description = "Order Progress"


# =========================
# SEPARATE STATUS PAGES
# =========================
@admin.register(PendingOrder)
class PendingOrderAdmin(BaseOrderAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status="pending")


@admin.register(ProcessingOrder)
class ProcessingOrderAdmin(BaseOrderAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status="processing")


@admin.register(ShippedOrder)
class ShippedOrderAdmin(BaseOrderAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status="shipped")


@admin.register(DeliveredOrder)
class DeliveredOrderAdmin(BaseOrderAdmin):
    actions = []  # Delivered orders locked

    def get_queryset(self, request):
        return super().get_queryset(request).filter(status="delivered")


@admin.register(CancelledOrder)
class CancelledOrderAdmin(BaseOrderAdmin):
    actions = []  # Cancelled orders locked

    def get_queryset(self, request):
        return super().get_queryset(request).filter(status="cancelled")


def send_invoice(order):
    pdf_path = generate_invoice(order)

    email = EmailMessage(
        subject="Your Invoice from The Fashion Flare",
        body="Hi,\n\nYour order has been delivered. Invoice is attached.\n\nThanks!",
        to=[order.user.email],
    )
    email.attach_file(pdf_path)
    email.send()