from django.shortcuts import get_object_or_404, render, redirect
from django.utils.timezone import now
from django.http import JsonResponse
from cart.models import Coupon
from products.models import ProductVariant


# =========================
# ADD TO CART
# =========================
def add_to_cart(request):
    if request.method != "POST":
        return JsonResponse({"success": False}, status=405)

    variant_id = request.POST.get("variant_id")
    quantity = int(request.POST.get("quantity", 1))

    variant = get_object_or_404(ProductVariant, id=variant_id)

    cart = request.session.get("cart", {})

    image = ""
    if variant.product.images.exists():
        image = variant.product.images.first().image.url

    if variant_id in cart:
        cart[variant_id]["quantity"] += quantity
    else:
        cart[variant_id] = {
            "variant_id": variant.id,
            "product": variant.product.name,
            "price": float(variant.discount_price or variant.price),
            "size": variant.size,
            "color": variant.color,
            "quantity": quantity,
            "image": image,
        }

    request.session["cart"] = cart
    request.session.modified = True

    return JsonResponse({
        "success": True,
        "cart_count": sum(item["quantity"] for item in cart.values())
    })


# =========================
# CART PAGE
# =========================
def cart_detail(request):
    cart = request.session.get("cart", {})

    subtotal = sum(
        item["price"] * item["quantity"]
        for item in cart.values()
    )

    # ✅ APPLY COUPON
    coupon = request.session.get("coupon")

    discount = 0
    coupon_code = None

    # ✅ Handle old coupon format (int) + new format (dict)
    if isinstance(coupon, dict):
        discount = coupon.get("discount", 0)
        coupon_code = coupon.get("code")
    elif isinstance(coupon, int):
        discount = coupon

    discount_amount = (subtotal * discount) / 100
    total = subtotal - discount_amount

    # ✅ ERROR MESSAGE (shown once)
    coupon_error = request.session.pop("coupon_error", None)

    return render(request, "cart/cart_detail.html", {
        "cart": cart,
        "subtotal": subtotal,
        "discount": discount,
        "discount_amount": discount_amount,
        "total": total,
        "coupon_code": coupon_code,
        "coupon_error": coupon_error,
    })


# =========================
# REMOVE ITEM
# =========================
def cart_remove(request, variant_id):
    cart = request.session.get("cart", {})
    variant_id = str(variant_id)

    if variant_id in cart:
        del cart[variant_id]
        request.session["cart"] = cart
        request.session.modified = True

    return redirect("cart_detail")


# =========================
# APPLY COUPON
# =========================
def apply_coupon(request):
    if request.method == "POST":
        code = request.POST.get("coupon")

        try:
            coupon = Coupon.objects.get(
                code__iexact=code,
                active=True,
                expiry_date__gte=now().date()
            )
            request.session["coupon"] = {
                "code": coupon.code,
                "discount": coupon.discount_percent
            }
        except Coupon.DoesNotExist:
            request.session["coupon_error"] = "Invalid or expired coupon"

    return redirect("cart_detail")


# =========================
# REMOVE COUPON
# =========================
def remove_coupon(request):
    request.session.pop("coupon", None)
    return redirect("cart_detail")

def mini_cart(request):
    cart = request.session.get("cart", {})
    items = []

    for item in cart.values():
        items.append({
            "variant_id": item["variant_id"],
            "product": item["product"],
            "price": item["price"],
            "quantity": item["quantity"],
            "color": item["color"],
            "size": item["size"],
            "image": item["image"],
        })

    return JsonResponse({"items": items})