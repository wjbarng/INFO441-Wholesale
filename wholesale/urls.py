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