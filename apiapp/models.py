from django.db import models
from django.contrib.auth import get_user_model
import datetime
import sys

class discount(models.Model):
    percentage = models.DecimalField(default=0.00, max_digits=3, decimal_places=2)
    minQuan = models.IntegerField(default=0)
    maxQuan = models.IntegerField(default=sys.maxsize)
    # shipping?

class category(models.Model):
    name = models.CharField(default="", unique=True, max_length=250)
    description = models.CharField(default="", max_length=250)
    image = models.ImageField()

class products(models.Model):
    name = models.CharField(default="", unique=True, max_length=250)
    description = models.CharField(default="", max_length=250)
    image = models.ImageField()
    price = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    category = models.ForeignKey(category, on_delete=models.CASCADE)
    max_quantity = models.IntegerField(default=sys.maxsize)
    min_quantity_retail = models.IntegerField(default=0)

class prod_dis(models.Model):
    products = models.ForeignKey(products, on_delete=models.CASCADE)
    discount = models.ForeignKey(discount, on_delete=models.CASCADE)
    
class prod_order(models.Model):
    product = models.ForeignKey(products, on_delete=models.CASCADE)
    # order = models.ForeignKey(order, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)