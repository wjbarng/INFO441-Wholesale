from django.contrib import admin
from .models import Discount, Category, Products, BusinessApplication
from .models import Customers, Payment, ShippingAddress, ShippingMethod, Order, Cart


admin.site.register(Discount)
admin.site.register(Category)
admin.site.register(Products)
# admin.site.register(Prod_dis)
admin.site.register(Cart)
admin.site.register(Customers)
admin.site.register(Payment)
admin.site.register(ShippingAddress)
admin.site.register(ShippingMethod)
admin.site.register(Order)
admin.site.register(BusinessApplication)
