from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets

from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework.decorators import api_view
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt

from .models import Category, Discount, Payment, ShippingMethod, Products, Prod_dis, Customers, ShippingAddress, Order, Prod_order, Seller
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User

import json
import datetime

@csrf_exempt
def Category_view(request):
    if (request.method == "GET"):
        all_category = list(Category.objects.all().values())
        return JsonResponse(all_category, safe=False, status=status.HTTP_200_OK)
    elif (request.method == "POST"):
        try:
            data = json.loads(request.body.decode('utf-8'))
            if ('description' not in data.keys()):
                data['description'] = ""
            if ('image' not in data.keys()):
                data['image'] = null
            try:
                new_category = Category(name = data['name'],
                                        description = data['description'],
                                        image = data['image'])
                new_category.save()
            except:
                return HttpResponse('could not save into the databse', status = status.HTTP_400_BAD_REQUEST)
        except:
            return HttpResponse('Json Decode Error', status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(data, safe=False, status=status.HTTP_201_CREATED, 
                                        content_type='application/json')
    else:
        return HttpResponse('Unavailable Request', status = status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def Category__detail_view(request, category_id):
    if (request.method == "GET"):
        try:
            category_info = list(Category.objects.all().values().filter(id = category_id)))[0]
        except:
            return HttpResponse("category does not exist", status = status.HTTP_404_NOT_FOUND)
        return JsonResponse(category_info, safe=False, status = status.HTTP_200_OK, 
                                content_type = 'application/json')
    elif (request.method == "PATCH"):
        try:
            category_info = Category.objects.filter(id = category_id))
            category_info_values = category_info.get()
        except:
            return HttpResponse("category does not exist", status = status.HTTP_404_NOT_FOUND)
        try:
            data = json.loads(request.body.decode('utf-8'))
            if ('description' in data.keys()):
                category_info_values.description = data["description"]
            if ('image' in data.keys()):
                category_info_values.image = data["image"]
        except:
            return HttpResponse('Json Decode Error', status=status.HTTP_400_BAD_REQUEST)
        try:
            category_info_values.save()
            updated_category_info = list(category_info.values())[0]
            return JsonResponse(updated_category_info, safe=False, status = status.HTTP_201_CREATED, 
                                        content_type = 'application/json')
        except:
            return HttpResponse('Update failed', status=status.HTTP_400_BAD_REQUEST)
    elif (request.method = "DELETE"):
        category_info = Category.objects.filter(id = category_id)
        try:
            category_info_values = category.get()
        except:
            return HttpResponse("category does not exist", safe=False, status = status.HTTP_404_NOT_FOUND)
        category_info.delete()
    else:
        return HttpResponse('Unavailable Request', status = status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def Discount_view(request):
    if (request.method == "GET"):
        all_discounts = list(Discount.objects.all().values())
        return JsonResponse(all_discounts, safe=False, status=status.HTTP_200_OK)
    elif (request.method == "POST"):
        try:
            data = json.loads(request.body.decode('utf-8'))
        except:
            return HttpResponse('Json Decode Error', status=status.HTTP_400_BAD_REQUEST)
        try:
            new_discount = Discount(
                percentage = data['percentage'],
                minQuan = data['minQuan'],
                maxQuan = data['maxQuan'],
                disShipping = data['disShipping']
            )
            new_discount.save()
        except:
            return HttpResponse("could not save into the database", safe=False, status = status.HTTP_404_NOT_FOUND)
        return JsonResponse(data, safe=False, status=status.HTTP_201_CREATED, 
                                        content_type='application/json')
    else:
        return HttpResponse('Unavailable Request', status = status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def Discount_view(request):
    id ()

@csrf_exempt
def Product_view(request):
    if (request.method == "GET"):
        all_products = list(Products.objects.all().values())
        return JsonResponse(all_products, safe=False, status=status.HTTP_200_OK)

    elif (request.method == "POST"):
        try:
            data = json.loads(request.body.decode('utf-8'))
            if ('description' not in data.keys()):
                data['description'] = ""
            if ('image' not in data.keys()):
                data['image'] == null
            try:
                new_product = Products(name = data['name'],
                                        description = data['description'],
                                        image = data['image'],
                                        price = data['price'],
                                        category = data['category'],
                                        max_quantity = data['max_quantity'],
                                        min_quantity = data['min_quantity'])
                new_prodcut.save()
            except:
                return HttpResponse('could not save to the database', 
                            status=status.HTTP_400_BAD_REQUEST)
            # get discount info
            post_product = {
                name = data['name'],
                description = data['description'],
                image = data['image'],
                price = data['price'],
                category = data['category'],
                max_quantity = data['max_quantity'],
                min_quantity = data['min_quantity']
            }
            return JsonResponse(all_discounts, safe=False, status=status.HTTP_200_OK)
        except:
            return HttpResponse('json encoding failed', 
                            status=status.HTTP_400_BAD_REQUEST)
            
    else:
        return HttpResponse('Unavailable Request', status = status.HTTP_400_BAD_REQUEST)

def Product_detail_view(request, product_id):
    if (request.method == "GET"):

    elif (request.method = "PATCH"):

    elif (request.method == "DELETE"):

    else:
        return HttpResponse('Unavailable Request', status = status.HTTP_400_BAD_REQUEST)
