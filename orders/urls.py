from django.urls import path
from .views import (
    checkout,
    place_order,
    create_razorpay_order,
    verify_payment,
)
from . import views


app_name = "orders"

urlpatterns = [
    path("checkout/", checkout, name="checkout"),
    path("place/", place_order, name="place_order"),
    path("pay/<int:order_id>/", create_razorpay_order, name="pay"),
    path("verify-payment/", verify_payment, name="verify_payment"),
    path("payment-success/", views.payment_success, name="payment_success"),
]
