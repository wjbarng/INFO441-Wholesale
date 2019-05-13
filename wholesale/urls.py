from django.conf.urls import url
from .views import Discount_view, Category_view, Product_view, Product_detail_view, Category_detail_view

#These two added for viewsets
# from django.conf.urls import include
from rest_framework.routers import DefaultRouter
# from .models import Discount_view, Category_view, Product_view, Product_detail_view
from django.urls import path, include

router = DefaultRouter()
urlpatterns = [
path('discounts', Discount_view, name='discount'),
path('categories', Category_view, name='category'),
path('categories/<int:category_id>', Category_detail_view, name='category detail'),
path('products', Product_view, name='product'),
path('product/<int:product_id>', Product_detail_view, name='product detail'),
]
