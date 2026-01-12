from django.urls import path
from . import views
from .views import orders_view



app_name = "accounts"

urlpatterns = [
    path("profile/", views.profile_view, name="profile"),
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("wishlist/toggle/<int:product_id>/", views.toggle_wishlist, name="toggle_wishlist"),
    path("orders/", views.orders_view, name="orders"),
    path("addresses/", views.address_list, name="addresses"),
path("addresses/add/", views.address_create, name="address_add"),
path("addresses/<int:pk>/edit/", views.address_edit, name="address_edit"),
path("addresses/<int:pk>/delete/", views.address_delete, name="address_delete"),
]
