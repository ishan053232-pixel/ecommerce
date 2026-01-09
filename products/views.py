from django.shortcuts import render, get_object_or_404,redirect
from .models import Product, ProductVariant, Category,ProductReview
from django.http import JsonResponse
from accounts.models import Wishlist
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from .forms import ReviewForm
from .utils import user_purchased_product
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    size_guide = getattr(product, "size_guide", None)

    # =============================
    # ✅ SIZE GUIDE ROWS (PARSED)
    # =============================
    size_guide_rows = []

    if size_guide and size_guide.content:
        for line in size_guide.content.splitlines():
            line = line.strip()
            if not line:
                continue

            parts = [p.strip() for p in line.split()]
            if len(parts) >= 3:
                size_guide_rows.append({
                    "size": parts[0],
                    "chest": parts[1],
                    "length": parts[2],
                })


    # =============================
    # ✅ WISHLIST
    # =============================
    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(
            user=request.user,
            product=product
        ).exists()

    # =============================
    # ✅ PRODUCT IMAGES
    # =============================
    images = product.images.all()

    # =============================
    # ✅ VARIANTS
    # =============================
    variant_qs = ProductVariant.objects.filter(
        product=product,
        is_active=True
    )

    variants = [
        {
            "id": v.id,
            "size": v.size,
            "color": v.color,
            "price": v.price,
            "discount_price": v.discount_price,
            "stock": v.stock,
        }
        for v in variant_qs
    ]

    sizes = sorted({v["size"] for v in variants})

    colors = (
        ProductVariant.objects
        .filter(product=product, is_active=True)
        .values("color", "color_hex")
        .distinct()
    )

    images_by_color = {
        c["color"]: [img.image.url for img in images]
        for c in colors
    }

    # =============================
    # ✅ STOCK SCHEMA
    # =============================
    in_stock = variant_qs.filter(stock__gt=0).exists()
    schema_availability = (
        "https://schema.org/InStock"
        if in_stock
        else "https://schema.org/OutOfStock"
    )

    # =============================
    # ✅ RELATED PRODUCTS
    # =============================
    related_products = (
        Product.objects
        .filter(category=product.category, is_active=True)
        .exclude(id=product.id)[:4]
    )

    # =============================
    # ✅ CART COUNT
    # =============================
    cart = request.session.get("cart", {})
    cart_count = sum(item["quantity"] for item in cart.values())

    # =============================
    # ✅ STORY SECTIONS
    # =============================
    story_sections = product.story_sections.filter(is_active=True)

    # =====================================================
    # ⭐⭐⭐ REVIEWS & RATINGS (FULLY WORKING LOGIC)
    # =====================================================

    reviews = product.reviews.select_related("user").order_by("-created_at")
    average_rating = reviews.aggregate(avg=Avg("rating"))["avg"]

    can_review = False
    user_review = None
    review_form = None

    if request.user.is_authenticated:
        purchased = user_purchased_product(request.user, product)
        user_review = ProductReview.objects.filter(
            product=product,
            user=request.user
        ).first()

        if purchased and not user_review:
            can_review = True
            review_form = ReviewForm()

    # ✅ Handle review submission
    if request.method == "POST" and can_review:
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect("product_detail", slug=product.slug)

    # =============================
    # ✅ FINAL RENDER
    # =============================
    return render(request, "products/product_detail.html", {
        "product": product,
        "images": images,
        "variants": variants,
        "sizes": sizes,
        "colors": colors,
        "images_by_color": images_by_color,
        "related_products": related_products,
        "cart_count": cart_count,
        "story_sections": story_sections,
        "schema_availability": schema_availability,
        "is_wishlisted": is_wishlisted,
        "size_guide": size_guide,
        "size_guide_rows": size_guide_rows,


        # ⭐ REVIEWS
        "reviews": reviews,
        "average_rating": average_rating,
        "can_review": can_review,
        "user_review": user_review,
        "review_form": review_form,
    })



def search_view(request):
    query = request.GET.get("q", "").strip()

    products = Product.objects.filter(is_active=True)

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    categories = Category.objects.all()

    cart = request.session.get("cart", {})
    cart_count = sum(item["quantity"] for item in cart.values())

    return render(request, "products/search_results.html", {
        "query": query,
        "products": products,
        "categories": categories,
        "cart_count": cart_count,
    })

@require_POST
@login_required
def submit_review_ajax(request, slug):
    product = get_object_or_404(Product, slug=slug)

    # Security checks
    if not user_purchased_product(request.user, product):
        return JsonResponse({"error": "Not allowed"}, status=403)

    if ProductReview.objects.filter(product=product, user=request.user).exists():
        return JsonResponse({"error": "Already reviewed"}, status=400)

    form = ReviewForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()

        reviews = product.reviews.select_related("user")
        average_rating = product.average_rating

        html = render_to_string(
            "products/partials/review_list.html",
            {
                "reviews": reviews,
                "average_rating": average_rating,
            },
            request=request
        )

        return JsonResponse({
            "success": True,
            "html": html,
        })

    return JsonResponse({"error": "Invalid data"}, status=400)
