from django.urls import path
from . import views
from .views import orders_view



app_name = "accounts"

urlpatterns = [
    path("profile/", views.profile_view, name="profile"),
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("wishlist/toggle/<int:product_id>/", views.toggle_wishlist, name="toggle_wishlist"),
    path("orders/", views.orders_view, name="orders"),
]
