from django.shortcuts import render, get_object_or_404
from .models import Product, ProductVariant, Category
from django.http import JsonResponse
from accounts.models import Wishlist
from django.db.models import Q

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    # ✅ Wishlist state
    is_wishlisted = False
    if request.user.is_authenticated:
        is_wishlisted = Wishlist.objects.filter(
            user=request.user,
            product=product
        ).exists()

    # Product images
    images = product.images.all()

    # Variants queryset
    variant_qs = ProductVariant.objects.filter(
        product=product,
        is_active=True
    )

    # JSON-safe variants
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

    # Unique sizes
    sizes = sorted({v["size"] for v in variants})

    # Unique colors with hex
    colors = (
        ProductVariant.objects
        .filter(product=product, is_active=True)
        .values("color", "color_hex")
        .distinct()
    )

    # Images grouped by color
    images_by_color = {
        c["color"]: [img.image.url for img in images]
        for c in colors
    }

    # Schema availability
    in_stock = variant_qs.filter(stock__gt=0).exists()
    schema_availability = (
        "https://schema.org/InStock"
        if in_stock
        else "https://schema.org/OutOfStock"
    )

    # Related products
    related_products = (
        Product.objects
        .filter(category=product.category, is_active=True)
        .exclude(id=product.id)[:4]
    )

    # Cart count
    cart = request.session.get("cart", {})
    cart_count = sum(item["quantity"] for item in cart.values())

    # Story sections
    story_sections = product.story_sections.filter(is_active=True)

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
        "is_wishlisted": is_wishlisted,  # ✅ FINAL
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