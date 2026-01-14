from django.urls import path

from . import views
from .views import add_to_cart, cart_detail, cart_remove

urlpatterns = [
    path('', cart_detail, name='cart_detail'),
    path("add/", views.add_to_cart, name="add_to_cart"),
    path('remove/<int:variant_id>/', cart_remove, name='cart_remove'),
    path("apply-coupon/", views.apply_coupon, name="apply_coupon"),
    path("remove-coupon/", views.remove_coupon, name="remove_coupon"),
    path("mini/", views.mini_cart, name="mini_cart"),

]
