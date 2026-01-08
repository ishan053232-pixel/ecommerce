from django.db import models

class HeroSlide(models.Model):
    CATEGORY_CHOICES = (
        ("all", "All"),
        ("mens", "Mens"),
        ("womens", "Womens"),
    )

    tag = models.CharField(max_length=50)
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to="hero/")
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="all"
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.title} ({self.category})"
