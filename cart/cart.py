class Cart:
    def __init__(self, request):
        self.cart = request.session.get("cart", {})

    def __iter__(self):
        for item in self.cart.values():
            yield item

    def get_total_price(self):
        return sum(item["price"] * item["quantity"] for item in self.cart.values())

    def clear(self):
        self.cart.clear()
