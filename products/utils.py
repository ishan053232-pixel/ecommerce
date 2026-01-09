from orders.models import OrderItem

def user_purchased_product(user, product):
    return OrderItem.objects.filter(
        order__user=user,
        order__paid=True,
        product=product
    ).exists()
