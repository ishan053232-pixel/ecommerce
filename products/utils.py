from orders.models import Order, OrderItem

def user_purchased_product(user, product):
    return OrderItem.objects.filter(
        order__user=user,
        product=product,
        order__status="delivered"   # ✅ use status, NOT paid
    ).exists()
