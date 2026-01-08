from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from products.models import ProductVariant
from django.shortcuts import redirect

# =========================
# ADD TO CART
# =========================
def add_to_cart(request):
    if request.method == "POST":
        variant_id = str(request.POST.get("variant_id"))
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

    return JsonResponse({"success": False})


# =========================
# CART PAGE
# =========================
def cart_detail(request):
    cart = request.session.get("cart", {})

    subtotal = sum(
        item["price"] * item["quantity"]
        for item in cart.values()
    )

    total = subtotal  # shipping free

    return render(request, "cart/cart_detail.html", {
        "cart": cart,
        "subtotal": subtotal,
        "total": total,
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

    return JsonResponse({"success": True})

def cart_remove(request, variant_id):
    cart = request.session.get("cart", {})
    variant_id = str(variant_id)

    if variant_id in cart:
        del cart[variant_id]
        request.session["cart"] = cart
        request.session.modified = True

    return redirect('cart_detail')  # 👈 IMPORTANT