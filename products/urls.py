from django.urls import path
from .views import product_detail,search_view
from . import views


urlpatterns = [
     path("search/", views.search_view, name="product_search"),
    path("<slug:slug>/", views.product_detail, name="product_detail"),
   path("review/<slug:slug>/",views.submit_review_ajax, name="submit_review_ajax"),
]
