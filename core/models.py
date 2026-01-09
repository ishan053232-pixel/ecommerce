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


class HomeVideo(models.Model):
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional heading shown over video"
    )
    subtitle = models.TextField(
        blank=True,
        help_text="Optional description text"
    )
    video = models.FileField(
        upload_to="home_videos/",
        help_text="Upload MP4 video (muted, short)"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Homepage Video"
        verbose_name_plural = "Homepage Video"

    def __str__(self):
        return self.title or "Homepage Video"


