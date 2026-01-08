from products.models import Category

def navbar_categories(request):
    return {
        "categories": Category.objects.filter(is_active=True)
    }
