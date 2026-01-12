import uuid
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import Order, OrderItem
import razorpay
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


@login_required
def place_order(request):
    cart = request.session.get("cart", {})
    if not cart:
        return redirect("cart_detail")

    order = Order.objects.create(
        user=request.user,
        order_id=f"TFF-{uuid.uuid4().hex[:8].upper()}",
        total_amount=sum(
            item["price"] * item["quantity"] for item in cart.values()
        ),
        status="pending"
    )

    for item in cart.values():
        OrderItem.objects.create(
            order=order,
            product_id=item["product_id"],
            variant_id=item["variant_id"],
            quantity=item["quantity"],
            price=item["price"]
        )

    # clear cart
    request.session["cart"] = {}

    return redirect("accounts:orders")

@login_required
def checkout(request):
    cart = request.session.get("cart", {})


    if len(cart) == 0:
        return redirect("cart_detail")

    total_amount = sum(
    item["price"] * item["quantity"]
    for item in cart.values()
)


    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    razorpay_order = client.order.create({
        "amount": int(total_amount * 100),  # INR → paise
        "currency": "INR",
        "payment_capture": 1
    })

    return render(request, "orders/checkout.html", {
        "cart": cart,
        "total_amount": total_amount,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": razorpay_order["id"],
    })

@csrf_exempt
def payment_success(request):
    if request.method == "POST":
        user = request.user
        cart = request.session.get("cart", {})


        order = Order.objects.create(
            user=user,
            total_amount=cart.get_total_price(),
            status="pending",  # admin will ship later
            payment_status="paid"
        )

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                quantity=item["quantity"],
                price=item["price"]
            )

        cart.clear()
        return redirect("accounts:orders")
