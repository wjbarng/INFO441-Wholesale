from django.db import models
import sys
from django.contrib.auth.models import User

class Payment(models.Model):
    CardNumber = models.IntegerField()
    Name = models.CharField(max_length=50)

class ShippingMethod(models.Model):
    ShipMethName = models.CharField(max_length = 80, unique=True)
    ShipMethDesc = models.TextField(max_length=250)
    ShipMethPrice = models.DecimalField(max_digits=10, decimal_places=2)

class Category(models.Model):
    CATEGORY_CHOICES = (
        ('Pantry & Dry Goods', 'Pantry & Dry Goods'),
        ('Bath & Facial Tissue', 'Bath & Facial Tissue'),
        ('Canned Goods', 'Canned Goods'),
        ('Cleaning Products', 'Cleaning Products'),
        ('Coffee & Sweeteners', 'Coffee & Sweeteners'),
        ('Emergency Kits & Supplies', 'Emergency Kits & Supplies'),
        ('Breakroom Serving Supplies', 'Breakroom Serving Supplies'),
        ('Gourmet Foods', 'Gourmet Foods'),
        ('Paper Towels', 'Paper Towels'),
        ('Snacks', 'Snacks'),
        ('Water & Beverages', 'Water & Beverages'),
    )
    name = models.CharField(default='Pantry & Dry Goods', choices=CATEGORY_CHOICES, max_length=50)
    image = models.URLField(null=True, max_length=200)

class Products(models.Model):
    name = models.CharField(default="", unique=True, max_length=250)
    description = models.CharField(default="", max_length=250)
    image = models.URLField(null=True, max_length=200)
    price = models.FloatField(default=0.00)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    max_quantity = models.IntegerField(default=sys.maxsize)
    min_quantity_retail = models.IntegerField(default=0)

class Discount(models.Model):
    percentage = models.FloatField(default=0.00)
    minQuan = models.IntegerField(default=0)
    maxQuan = models.IntegerField(default=sys.maxsize)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)

class Customers(models.Model):
    user = models.OneToOneField(User, default = 1, on_delete=models.CASCADE)
    custFName = models.CharField(null=True, max_length=50)
    custLName = models.CharField(null = True, max_length=50)
    custAddress = models.CharField(max_length = 80)
    custCity = models.CharField(max_length = 50)
    custState = models.CharField(max_length = 2)
    custZip = models.CharField(max_length = 20)
    custPhone = models.CharField(max_length = 20)
    businessName = models.CharField(null = True, max_length=50)
    PaymentID = models.ForeignKey(Payment, null=True, on_delete=models.CASCADE)
    custLevel = models.IntegerField(default = 1) 

class Cart(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    prodName = models.ForeignKey(Products, on_delete=models.CASCADE)
    prodQuantity = models.IntegerField()

class ShippingAddress(models.Model):
    custID = models.ForeignKey(Customers, on_delete=models.CASCADE)
    shipAddFname = models.CharField(null=True, max_length=50)
    shipAddLname = models.CharField(null=True, max_length=50)
    businessName = models.CharField(null=True, max_length=50)
    shipAddAddress = models.CharField(max_length = 80)
    shipAddCity = models.CharField(max_length = 50)
    shipAddState = models.CharField(max_length = 2)
    shipAddZip = models.CharField(max_length = 20)
    shipAddPhone = models.CharField(max_length = 20)


class Order(models.Model):
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    orderDate = models.DateField()
    shippedDate = models.DateField()
    totalPrice = models.DecimalField(max_digits=10, decimal_places=2)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    shippingMethod = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE)
    shippingAddress = models.ForeignKey(ShippingAddress, on_delete=models.CASCADE)


class BusinessApplication(models.Model):
    busName = models.CharField(max_length=30)
    busAddress = models.CharField(max_length=30)
    busZip = models.CharField(max_length=30)
    busCity = models.CharField(max_length=30)
    busState = models.CharField(max_length=2)
    busEmail = models.EmailField(max_length=30)
    busPhone = models.CharField(max_length=30)