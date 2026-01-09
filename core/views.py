from django.shortcuts import render
from products.models import Product, Category
from core.models import HeroSlide
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import HomeVideo


def home(request):
    category_slug = request.GET.get("category", "all")
    sub_slug = request.GET.get("sub")
    query = request.GET.get("q")

    categories = Category.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)

    # Filter by category
    if category_slug != "all":
        products = products.filter(subcategory__category__slug=category_slug)

    # Filter by sub-category
    if sub_slug:
        products = products.filter(subcategory__slug=sub_slug)

    # Search
    if query:
        products = products.filter(name__icontains=query)

    hero_slides = HeroSlide.objects.filter(
        is_active=True,
        category__in=["all", category_slug]
    ).order_by("order")

    home_video = HomeVideo.objects.filter(is_active=True).first()

    cart = request.session.get("cart", {})
    cart_count = sum(item["quantity"] for item in cart.values()) if cart else 0

    return render(
        request,
        "home.html",
        {
            "categories": categories,
            "products": products,
            "hero_slides": hero_slides,
            "home_video": home_video,
            "cart_count": cart_count,
            "active_category": category_slug,
            "active_sub": sub_slug,
        }
    )


def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST["username"],
            password=request.POST["password"]
        )
        if user:
            login(request, user)
            return redirect("home")
        messages.error(request, "Invalid username or password")
    return render(request, "accounts/login.html")


def register_view(request):
    if request.method == "POST":
        if request.POST["password1"] != request.POST["password2"]:
            messages.error(request, "Passwords do not match")
        else:
            User.objects.create_user(
                username=request.POST["username"],
                email=request.POST["email"],
                password=request.POST["password1"]
            )
            messages.success(request, "Account created successfully")
            return redirect("login")

    return render(request, "accounts/register.html")

def logout_view(request):
    logout(request)
    return redirect("home")

@login_required
def profile_view(request):
    return render(request, "accounts/profile.html")


@login_required
def orders_view(request):
    return render(request, "accounts/orders.html")

@login_required(login_url="login")
def checkout(request):
    # temporary placeholder
    return render(request, "checkout.html")



