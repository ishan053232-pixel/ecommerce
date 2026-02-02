import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.conf import settings


def generate_invoice(order):
    print("🔥 generate_invoice() CALLED")
    print("👉 Order ID:", order.order_id)

    invoice_dir = os.path.join(settings.MEDIA_ROOT, "invoices")
    print("📁 Invoice dir:", invoice_dir)

    os.makedirs(invoice_dir, exist_ok=True)

    file_path = os.path.join(invoice_dir, f"invoice_{order.order_id}.pdf")
    print("📄 Invoice file path:", file_path)

    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "The Fashion Flare")

    c.setFont("Helvetica", 12)
    c.drawString(50, height - 90, f"Invoice for Order #{order.order_id}")
    c.drawString(50, height - 120, f"Customer: {order.user.username}")
    c.drawString(50, height - 150, f"Total: ₹{order.total_amount}")
    c.drawString(50, height - 180, f"Status: {order.status.capitalize()}")

    y = height - 230
    for item in order.items.all():
        c.drawString(
            50,
            y,
            f"{item.product.name} x {item.quantity} = ₹{item.price}",
        )
        y -= 20

    c.showPage()
    c.save()

    print("✅ INVOICE GENERATED SUCCESSFULLY")
