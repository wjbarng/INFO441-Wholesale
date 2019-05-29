from django.conf.urls import url
from .views import Discount_view, Category_view, Product_view, Product_detail_view, Category_detail_view

#These two added for viewsets
# from django.conf.urls import include
from rest_framework.routers import DefaultRouter
# from .models import Discount_view, Category_view, Product_view, Product_detail_view
from django.urls import path, include
from django.contrib import admin
from . import views

router = DefaultRouter()
urlpatterns = [
    path('api/discounts', Discount_view, name='discount'),
    path('api/categories', Category_view, name='category api'),
    path('api/categories/<int:category_id>', Category_detail_view, name='category detail'),
    path('api/products', Product_view, name='product'),
    path('api/products/<int:product_id>', Product_detail_view, name='product detail api'),
    path('', views.homepage, name='home'), 
    path('categories', views.categories, name='category'),
    path('categories/<int:category_id>/products', views.products, name='products'), 
    path('categories/<int:category_id>/products/<int:product_id>', views.product_detail, name='product detail'), 
    path('products/register', views.product_regi, name="product register"),
    path('cart/', views.cart, name='cart'),
    path('about/', views.about, name='about'),
    path('support/', views.support, name='support'),
    path('signin/', views.signin, name='signin'),
    path('register/', views.register, name='register'),
    path('signout/', views.signout, name='signout'),
    path('account/', views.account, name='account'),
    path('payment/', views.payment, name='payment'),
    path('shipping/', views.shipping, name='shipping'),
    path('application/', views.application, name='application'),
]
