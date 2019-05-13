<<<<<<< HEAD
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
=======
from . import views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', views.homepage, name='home'), 
    path('product/', views.products, name='products'), 
    path('wholesale/', views.wholesale, name='wholesale'),
    path('about/', views.about, name='about'),
    path('support/', views.support, name='support'),
    path('signin/', views.signin, name='signin'),
    path('register/', views.register, name='register'),
    path('signout/', views.signout, name='signout'),
    path('account/', views.account, name='account'),
    path('shipping/', views.shipping, name='shipping'),
]
>>>>>>> origin/stanley-1
