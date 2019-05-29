from django.contrib import admin
from .models import Discount, Category, Products, Prod_dis, BusinessApplication
from .models import Prod_order, Customers, Payment, ShippingAddress, ShippingMethod, Order


admin.site.register(Discount)
admin.site.register(Category)
admin.site.register(Products)
admin.site.register(Prod_dis)
admin.site.register(Prod_order)
admin.site.register(Customers)
admin.site.register(Payment)
admin.site.register(ShippingAddress)
admin.site.register(ShippingMethod)
admin.site.register(Order)
# admin.site.register(Seller)
admin.site.register(BusinessApplication)
