from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from orders.utils.invoice import generate_invoice


@receiver(post_save, sender=Order)
def generate_invoice_on_delivery(sender, instance, created, **kwargs):
    if instance.status == "delivered":
        generate_invoice(instance)
