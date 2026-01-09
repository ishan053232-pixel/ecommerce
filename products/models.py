from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


# ==========================
# MAIN CATEGORY (MEN / WOMEN)
# ==========================
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


# ==========================
# SUB CATEGORY (T-Shirts etc.)
# ==========================
class SubCategory(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="subcategories"
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField()

    class Meta:
        unique_together = ("category", "slug")
        verbose_name_plural = "Sub Categories"

    def __str__(self):
        return f"{self.category.name} → {self.name}"


# ==========================
# PRODUCT
# ==========================
class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )
    subcategory = models.ForeignKey(
        SubCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    # ======================
    # STORY SECTION (ADMIN)
    # ======================
    style_title = models.CharField(
        max_length=255,
        default="Designed for everyday layering"
    )
    style_description = models.TextField(
        blank=True,
        help_text="Story text shown below product details"
    )

    # ======================
    # PRICING
    # ======================
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    # ======================
    # SEO (✅ FIXED LOCATION)
    # ======================
    meta_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="SEO title (leave blank to use product name)"
    )
    meta_description = models.TextField(
        blank=True,
        help_text="SEO meta description"
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_display_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def average_rating(self):
        """
        Returns average rating or None
        """
        return self.reviews.aggregate(avg=Avg("rating"))["avg"]


# ==========================
# PRODUCT VARIANT
# ==========================
class ProductVariant(models.Model):
    SIZE_CHOICES = [
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="variants"
    )

    size = models.CharField(max_length=5, choices=SIZE_CHOICES)

    color = models.CharField(
        max_length=15,
        help_text="Example: Black, Olive Green, Wine Red"
    )

    color_hex = models.CharField(
        max_length=7,
        blank=True,
        null=True,
        help_text="Example: #000000"
    )

    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"{self.product.name} - {self.size} - {self.color}"


# ==========================
# PRODUCT IMAGE
# ==========================
class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images"
    )
    image = models.ImageField(upload_to="products/")
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return self.product.name


# ==========================
# PRODUCT STORY SECTIONS
# ==========================
class ProductStorySection(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="story_sections"
    )

    title = models.CharField(
        max_length=255,
        help_text="Section heading (e.g. Designed for everyday layering)"
    )
    description = models.TextField(
        help_text="Section content"
    )

    position = models.PositiveIntegerField(
        default=0,
        help_text="Order of appearance"
    )

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return f"{self.product.name} → {self.title}"


# ==========================
# PRODUCT REVIEW ⭐⭐⭐⭐⭐
# ==========================
class ProductReview(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reviews"
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("product", "user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating})"


class ProductSizeGuide(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="size_guide"
    )

    title = models.CharField(
        max_length=200,
        default="Size Guide"
    )

    content = models.TextField(
        help_text="Use line breaks or table-style text"
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Size Guide – {self.product.name}"
