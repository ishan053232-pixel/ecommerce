from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from products.models import Product
from products.models import Category
from .models import Wishlist
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from orders.models import Order


# ==============================
def profile_view(request):
    categories = Category.objects.all()

    cart = request.session.get("cart", {})
    cart_count = sum(item["quantity"] for item in cart.values())

    return render(request, "accounts/profile.html", {
        "categories": categories,
        "cart_count": cart_count,
    })



# 🔹 Helper for navbar data
def navbar_context(request):
    categories = Category.objects.all()
    cart = request.session.get("cart", {})
    cart_count = sum(item["quantity"] for item in cart.values())
    return {
        "categories": categories,
        "cart_count": cart_count,
    }


# ==============================
# PROFILE
# ==============================
@login_required
def profile_view(request):
    context = navbar_context(request)
    return render(request, "accounts/profile.html", context)


# ==============================
# WISHLIST PAGE
# ==============================
@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(
        user=request.user
    ).select_related("product")

    return render(request, "accounts/wishlist.html", {
        "items": items,
        "categories": Category.objects.all(),
    })


# ==============================
# ORDERS PAGE
# ==============================
@login_required
def orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")

    return render(request, "accounts/orders.html", {
        "orders": orders,
        "categories": Category.objects.all(),
    })


# ==============================
# TOGGLE WISHLIST
# ==============================
@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    obj, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        obj.delete()
        added = False
    else:
        added = True

    return JsonResponse({"added": added})


#   ==============================    
# ORDERS PAGE
@login_required
def orders_view(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items__product")
        .order_by("-created_at")
    )

    return render(request, "accounts/orders.html", {
        "orders": orders
    })