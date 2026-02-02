import uuid
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from httpcore import request
from .models import Order, OrderItem
import razorpay
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from products.models import Product
from accounts.models import Address





@login_required
def place_order(request):
    cart = request.session.get("cart", {})
    address = request.POST.get("address")

    if not cart or not address:
        return redirect("orders:checkout")

    order = Order.objects.create(
        user=request.user,
        shipping_address=address,
        total_amount=sum(item["price"] * item["quantity"] for item in cart.values()),
        status="pending"
    )

    for item in cart.values():
        OrderItem.objects.create(
            order=order,
            product_id=item["product_id"],
            quantity=item["quantity"],
            price=item["price"]
        )

    return redirect("orders:pay", order.id)


@login_required
def checkout(request):
    cart = request.session.get("cart", {})

    if not cart:
        return redirect("cart_detail")

    total_amount = sum(
        item["price"] * item["quantity"] for item in cart.values()
    )

    # ✅ 1. Create DB order FIRST
    order = Order.objects.create(
        user=request.user,
        total_amount=total_amount,
        status="pending",
    )

    # Create order items
    for item in cart.values():
        OrderItem.objects.create(
            order=order,
            product_id=item["product_id"],
            quantity=item["quantity"],
            price=item["price"],
        )

    # ✅ 2. Create Razorpay order
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    razorpay_order = client.order.create({
        "amount": int(total_amount * 100),
        "currency": "INR",
        "payment_capture": 1,
    })

    # ✅ 3. SAVE razorpay_order_id
    order.razorpay_order_id = razorpay_order["id"]
    order.save()

    return render(request, "orders/checkout.html", {
        "order": order,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": razorpay_order["id"],
        "total_amount": total_amount,
    })

@csrf_exempt
def payment_success(request):
    if request.method != "POST":
        return redirect("accounts:orders")

    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_signature = request.POST.get("razorpay_signature")

    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
        return redirect("accounts:orders")

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    try:
        # ✅ VERIFY SIGNATURE
        client.utility.verify_payment_signature({
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        })

        # ✅ UPDATE ORDER
        order = Order.objects.get(razorpay_order_id=razorpay_order_id)
        order.razorpay_payment_id = razorpay_payment_id
        order.razorpay_signature = razorpay_signature
        order.is_paid = True
        order.status = "processing"
        order.save()

        # ✅ CLEAR CART
        request.session["cart"] = {}

        return redirect("accounts:orders")

    except Exception as e:
        print("Payment verification failed:", e)
        return redirect("orders:checkout")


@login_required
def checkout(request):
    cart = request.session.get("cart", {})

    if not cart:
        return redirect("cart_detail")

    # ✅ TOTAL
    total_amount = sum(
        item["price"] * item["quantity"]
        for item in cart.values()
    )

    # ✅ ADDRESS
    addresses = Address.objects.filter(user=request.user)
    default_address = addresses.filter(is_default=True).first() or addresses.first()

    if not default_address:
        return redirect("accounts:add_address")

    shipping_address = (
        f"{default_address.full_name}\n"
        f"{default_address.address_line_1}\n"
        f"{default_address.city}, {default_address.state} - {default_address.postal_code}\n"
        f"Phone: {default_address.phone}"
    )

    # ✅ CREATE ORDER
    order = Order.objects.create(
        user=request.user,
        total_amount=total_amount,
        status="pending",
        shipping_address=shipping_address,
    )

    # ✅ CREATE ORDER ITEMS (SAFE MODE)
    for key, item in cart.items():

        # 🔐 FIND PRODUCT ID SAFELY
        product_id = item.get("product_id")

        if not product_id:
            # fallback: key itself might be the product id
            try:
                product_id = int(key)
            except ValueError:
                continue  # skip invalid cart entries

        product = Product.objects.filter(id=product_id).first()

        if not product:
            continue  # skip broken cart item instead of crashing

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=item["quantity"],
            price=item["price"],
            size=item.get("size"),
        )

    # ✅ RAZORPAY
    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    razorpay_order = client.order.create({
        "amount": int(total_amount * 100),
        "currency": "INR",
        "payment_capture": 1
    })

    order.razorpay_order_id = razorpay_order["id"]
    order.save()

    return render(request, "orders/checkout.html", {
        "order": order,
        "cart_items": order.items.all(),
        "total_amount": total_amount,
        "addresses": addresses,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": razorpay_order["id"],
    })



# =========================
# VERIFY PAYMENT (Razorpay callback)
# =========================
@csrf_exempt
def verify_payment(request):
    if request.method != "POST":
        return JsonResponse({"status": "invalid"})

    data = json.loads(request.body)

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    try:
        client.utility.verify_payment_signature(data)

        order = Order.objects.get(
            razorpay_order_id=data["razorpay_order_id"]
        )

        order.razorpay_payment_id = data["razorpay_payment_id"]
        order.razorpay_signature = data["razorpay_signature"]
        order.is_paid = True
        order.status = "processing"
        order.save()

        # ✅ Clear cart AFTER success
        request.session["cart"] = {}

        return JsonResponse({"status": "success"})

    except Exception as e:
        return JsonResponse({"status": "failed", "error": str(e)})
    

@login_required
def create_razorpay_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    client = razorpay.Client(auth=(
        settings.RAZORPAY_KEY_ID,
        settings.RAZORPAY_KEY_SECRET
    ))

    razorpay_order = client.order.create({
        "amount": int(order.total_amount * 100),
        "currency": "INR",
        "payment_capture": 1
    })

    order.razorpay_order_id = razorpay_order["id"]
    order.save()

    return render(request, "orders/payment.html", {
        "order": order,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": razorpay_order["id"],
        "amount": int(order.total_amount * 100),
    })

