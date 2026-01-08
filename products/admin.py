from django.contrib import admin
from django.utils.html import format_html
from adminsortable2.admin import (
    SortableAdminBase,
    SortableAdminMixin,
    SortableInlineAdminMixin,
)

from .models import (
    Category,
    SubCategory,
    Product,
    ProductVariant,
    ProductImage,
    ProductStorySection,
)

# ==========================
# PRODUCT IMAGE INLINE
# ==========================
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="60" style="border-radius:6px;" />',
                obj.image.url
            )
        return "-"


# ==========================
# PRODUCT VARIANT INLINE
# ==========================
class ProductVariantInline(SortableInlineAdminMixin, admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = (
        "size",
        "color",
        "color_hex",
        "price",
        "discount_price",
        "stock",
        "is_active",
    )


# ==========================
# PRODUCT STORY INLINE
# ==========================
class ProductStoryInline(SortableInlineAdminMixin, admin.StackedInline):
    model = ProductStorySection
    extra = 1
    fields = ("title", "description", "is_active", "position")


# ==========================
# PRODUCT ADMIN (SINGLE SOURCE OF TRUTH)
# ==========================
@admin.register(Product)
class ProductAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = ("name", "subcategory", "price", "is_active", "stock_status")
    list_filter = ("subcategory", "is_active")
    prepopulated_fields = {"slug": ("name",)}

    inlines = [
        ProductImageInline,
        ProductVariantInline,
        ProductStoryInline,  # ✅ story sections here
    ]

    def stock_status(self, obj):
        total_stock = sum(v.stock for v in obj.variants.filter(is_active=True))
        if total_stock == 0:
            return format_html(
                '<span style="color:red;font-weight:bold;">OUT OF STOCK</span>'
            )
        elif total_stock < 10:
            return format_html(
                '<span style="color:orange;font-weight:bold;">LOW ({})</span>',
                total_stock
            )
        return format_html(
            '<span style="color:green;font-weight:bold;">IN STOCK</span>'
        )

    stock_status.short_description = "Stock"


# ==========================
# CATEGORY ADMIN
# ==========================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    prepopulated_fields = {"slug": ("name",)}


# ==========================
# SUB CATEGORY ADMIN
# ==========================
@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category")
    list_filter = ("category",)
    prepopulated_fields = {"slug": ("name",)}


# ==========================
# PRODUCT VARIANT ADMIN
# ==========================
@admin.register(ProductVariant)
class ProductVariantAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = (
        "product",
        "size",
        "color",
        "stock",
        "is_active",
        "price",
        "discount_price",
    )
    list_filter = ("is_active", "size", "color")
    search_fields = ("product__name",)


# ==========================
# PRODUCT IMAGE ADMIN
# ==========================
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "is_main")
    list_filter = ("is_main",)
