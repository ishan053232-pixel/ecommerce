from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from .models import Order


@receiver(pre_save, sender=Order)
def order_status_change_email(sender, instance, **kwargs):
    """
    Send email ONLY when order status changes
    """

    if not instance.pk:
        return  # new order → skip

    try:
        old_order = Order.objects.get(pk=instance.pk)
    except Order.DoesNotExist:
        return

    if old_order.status == instance.status:
        return  # status not changed

    user = instance.user
    order_id = instance.order_id
    new_status = instance.get_status_display()

    subject = f"Your Order #{order_id} is now {new_status}"

    message_map = {
        "pending": f"Hi {user.username},\n\nYour order #{order_id} has been placed successfully.",
        "processing": f"Hi {user.username},\n\nWe are processing your order #{order_id}.",
        "shipped": f"Hi {user.username},\n\nYour order #{order_id} has been shipped.",
        "delivered": f"Hi {user.username},\n\nYour order #{order_id} has been delivered. Enjoy!",
        "cancelled": f"Hi {user.username},\n\nYour order #{order_id} has been cancelled.",
        "refunded": f"Hi {user.username},\n\nYour order #{order_id} has been refunded.",
    }

    message = message_map.get(instance.status)

    if message:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
# Note: Ensure that email backend is configured in settings.py for sending emails.