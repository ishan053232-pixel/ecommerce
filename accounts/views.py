from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from products.models import Product, Category
from orders.models import Order
from .models import Wishlist, Address
from .forms import AddressForm
from django.contrib import messages

# ==============================
# NAVBAR CONTEXT (helper)
# ==============================
def navbar_context(request):
    categories = Category.objects.all()
    cart = request.session.get("cart", {})
    cart_count = sum(item["quantity"] for item in cart.values())
    return {
        "categories": categories,
        "cart_count": cart_count,
    }


# ==============================
# PROFILE PAGE
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
    items = Wishlist.objects.filter(user=request.user).select_related("product")

    context = navbar_context(request)
    context["items"] = items

    return render(request, "accounts/wishlist.html", context)


# ==============================
# CLEAR WISHLIST
# ==============================
@login_required
def clear_wishlist(request):
    if request.method == "POST":
        Wishlist.objects.filter(user=request.user).delete()
    return redirect("accounts:wishlist")


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


# ==============================
# ORDERS PAGE
# ==============================
@login_required
def orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")

    status = request.GET.get("status")

    if status:
        orders = orders.filter(status=status)

    return render(request, "accounts/orders.html", {
        "orders": orders,
    })


# ==============================
# ORDER DETAIL PAGE ✅ (FIXED)
# ==============================
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "accounts/order_detail.html", {"order": order})


# ==============================
# ADDRESSES
# ==============================
@login_required
def address_list(request):
    addresses = request.user.addresses.all()
    return render(request, "accounts/addresses.html", {"addresses": addresses})


@login_required
def address_create(request):
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user

            if address.is_default:
                Address.objects.filter(user=request.user, is_default=True).update(is_default=False)

            address.save()
            return redirect("accounts:addresses")
    else:
        form = AddressForm()

    return render(request, "accounts/address_form.html", {"form": form, "title": "Add Address"})


@login_required
def address_edit(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)

    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save(commit=False)

            if address.is_default:
                Address.objects.filter(user=request.user, is_default=True).exclude(pk=address.pk).update(is_default=False)

            address.save()
            return redirect("accounts:addresses")
    else:
        form = AddressForm(instance=address)

    return render(request, "accounts/address_form.html", {"form": form, "title": "Edit Address"})


@login_required
def address_delete(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    return redirect("accounts:addresses")



@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status in ['pending', 'processing']:
        order.status = 'cancelled'
        order.save()
        messages.success(request, "Order cancelled successfully.")
    else:
        messages.error(request, "This order cannot be cancelled.")

    return redirect('accounts:order_detail', order_id=order.id)

@login_required
def orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    status = request.GET.get("status")
    if status:
        orders = orders.filter(status=status)

    return render(request, "accounts/orders.html", {
        "orders": orders
    })
