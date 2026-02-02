from django.db import models
from django.contrib.auth.models import User
from products.models import Product
import uuid


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    order_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(
        max_length=100, blank=True, null=True
    )
    razorpay_payment_id = models.CharField(
        max_length=100, blank=True, null=True
    )
    razorpay_signature = models.CharField(
        max_length=255, blank=True, null=True
    )
    is_paid = models.BooleanField(default=False)
    # ✅ PAYMENT FIELDS
    is_paid = models.BooleanField(default=False)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)

    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = f"TFF-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} ({self.order.order_id})"


# =====================================================
# PROXY MODELS (ADMIN WORKFLOW VIEWS)
# =====================================================

class PendingOrder(Order):
    class Meta:
        proxy = True
        verbose_name = "Pending Order"
        verbose_name_plural = "Pending Orders"


class ProcessingOrder(Order):
    class Meta:
        proxy = True
        verbose_name = "Processing Order"
        verbose_name_plural = "Processing Orders"


class ShippedOrder(Order):
    class Meta:
        proxy = True
        verbose_name = "Shipped Order"
        verbose_name_plural = "Shipped Orders"


class DeliveredOrder(Order):
    class Meta:
        proxy = True
        verbose_name = "Delivered Order"
        verbose_name_plural = "Delivered Orders"


class CancelledOrder(Order):
    class Meta:
        proxy = True
        verbose_name = "Cancelled Order"
        verbose_name_plural = "Cancelled Orders"

        
