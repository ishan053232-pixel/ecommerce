from django.urls import path
from .views import add_to_cart, cart_detail, cart_remove

urlpatterns = [
    path('', cart_detail, name='cart_detail'),
    path('add/', add_to_cart, name='add_to_cart'),
    path('remove/<int:variant_id>/', cart_remove, name='cart_remove'),
]
