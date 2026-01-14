from django.db import models

# Create your models here.
class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.PositiveIntegerField()
    active = models.BooleanField(default=True)
    expiry_date = models.DateField()