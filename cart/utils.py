
from products.models import ProductVariant

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get("cart")
        if not cart:
            cart = self.session["cart"] = {}
        self.cart = cart

    def __iter__(self):
        for key, item in self.cart.items():
            item["variant_id"] = int(key)   # ✅ FIX HERE
            item["total_price"] = item["price"] * item["quantity"]
            yield item

    def __len__(self):
        return sum(item["quantity"] for item in self.cart.values())

    def get_subtotal(self):
        return sum(
            item["price"] * item["quantity"]
            for item in self.cart.values()
        )

    def get_total(self):
        return self.get_subtotal()
