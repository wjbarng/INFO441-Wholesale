from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .forms import RegistrationForm, ShippingAddressForm, ProductRegistrationForm, BusinessApplicationForm
from django.contrib.auth.models import User
from wholesale.models import Customers, Payment, ShippingAddress, BusinessApplication, Category, Discount, ShippingMethod, Products, Prod_dis, Order, Prod_order
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from decimal import Decimal

import json
import datetime

@csrf_exempt
def homepage(request):
	return render(request, "index.html", {})

@csrf_exempt
def products(request):
    if (request.method == "GET"):
        return render(request, "products.html", {})

@csrf_exempt
def product_detail(request, product_id):
    if (request.method == "GET"):
        try:
            product = Products.objects.all().filter(id = product_id).values()[0]
        except:
            return HttpResponse("Product does not exists.", status=404)
        try:
            category = Category.objects.all().filter(id = product['category_id']).values()[0]

        except:
            return HttpResponse("Category does not exists.", status=404)
        return HttpResponse(render(request, "productDetail.html", 
			{'product':product, 'category':category}), status=200)
    else:
        return HttpResponse("Method not allowed on /product/id.", status=405)

@csrf_exempt
def product_regi(request):
    if request.method == "POST":
        
        form = ProductRegistrationForm(request.POST)
        if form.is_valid():
            clean_data = form.clean()
            print(clean_data)
            try:
                try:
                    # connecting foerign key with Category
                    category = Category.objects.all().filter(name = clean_data['category'])[0]
                except:
                    return HttpResponse('Check category name', 
                        status=status.HTTP_400_BAD_REQUEST)
                new_product = Products(name = clean_data['name'],
                                    description = clean_data['description'],
                                    image = clean_data['image'],
                                    price = clean_data['price'],
                                    category = category,
                                    max_quantity = clean_data['max_quantity'],
                                    min_quantity_retail = clean_data['min_quantity_retail'])
                new_product.save()
                messages.success(request,('You have successfully registered'))
                return render(request, "products.html")
            except:
                messages.error(request,('Could not register product'))
                return HttpResponseRedirect('registerProduct')
        else:
            messages.error(request,('Form not valid'))
            HttpResponseRedirect('registerProduct')
    elif request.method == "GET":
        return render(request, "registerProduct.html", {'form': ProductRegistrationForm})

@csrf_exempt
def wholesale(request):
    return render(request, "wholesale.html", {})

@csrf_exempt
def about(request):
    return render(request, "about.html", {})

@csrf_exempt
def support(request):
    return render(request, "support.html", {})

""" Sign user in on post, update password on patch, or get sign in 
    form on get """
@csrf_exempt
@api_view(['GET', 'POST'])
def signin(request):
    """ Sign user in on post, update password on patch, or get sign in 
    form on get """
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['userpassword']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            messages.success(request,('You have successfully logged in'))
            return redirect('home')	
        else:
            messages.success(request,('User does not exist, either register or login again'))
            return redirect('signin')
    elif request.method == "GET":
        return render(request, "signin.html", {})

@csrf_exempt
def signout(request):
    logout(request)
    messages.success(request,('You have been logged out'))
    return redirect('home')			



""" Registers a new individual user on post, deletes user on delete,
    and gets the register form on get """
@csrf_exempt
@api_view(['GET', 'POST', 'DELETE'])
def register(request):
    """ Registers a new individual user on post, deletes user on delete,
    and gets the register form on get """
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['password'] != form.cleaned_data['passwordconf']:
                messages.error(request,('Password confirmation does not match password'))
                return render(request, "register.html", {'form': RegistrationForm})
            else:
                User.objects.create_user(username = form.cleaned_data['username'], email = form.cleaned_data['email'], password = form.cleaned_data['password'])

                user = User.objects.filter(username = form.cleaned_data['username']).get()
                customer = Customers.objects.create(user = user, custFName = form.cleaned_data['first_name'], custLName = form.cleaned_data['last_name'],
                custAddress = form.cleaned_data['custAddress'], custCity = form.cleaned_data['custCity'], custZip = form.cleaned_data['custZip'],
                custState = form.cleaned_data['custState'], custPhone = form.cleaned_data['custPhone'], custLevel = form.cleaned_data['custLevel'])
                customer.save()
                messages.success(request,('You have successfully registered'))
                return redirect('signin')
        else:
            messages.error(request,('Form not valid'))
            redirect('register')
    elif request.method == "DELETE":
        if request.user.is_authenticated:
            User.objects.filter(id = request.user.id).delete()
            Customers.objects.filter(user = request.user).delete()
            return HttpResponse("Delete successful")
    elif request.method == "GET":
        return render(request, "register.html", {'form': RegistrationForm})

@csrf_exempt
def Category_view(request):
    """ This view is an API for the categories"""
    if (request.method == "GET"):
        all_category = list(Category.objects.all().values())
        return JsonResponse(all_category, safe=False, status=status.HTTP_200_OK)
    elif (request.method == "POST"):
        if (Customers.objects.get(user_id = request.user.id).custLevel != 1):
            return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        try:
            # Get the data and check if the data is valid
            data = json.loads(request.body.decode('utf-8'))
            if ('description' not in data.keys()):
                data['description'] = ""
            if ('image' not in data.keys()):
                data['image'] = None
            try:
                # create new Category object
                new_category = Category(name = data['name'],
                                        description = data['description'],
                                        image = data['image'])
                # save into the database
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
def Category_detail_view(request, category_id):
    """ This view is an API for the category detail"""
    if (request.method == "GET"):
        try:
            category_info = Category.objects.all().values().get(id = category_id)
        except:
            return HttpResponse("category does not exist", status = status.HTTP_404_NOT_FOUND)
        # get the products in specific category
        category_products = Products.objects.all().filter(category_id = category_id).values()
        category_info['prodcuts'] = list(category_products)
        return JsonResponse(category_info, safe=False, status = status.HTTP_200_OK, 
                                content_type = 'application/json')
    elif (request.method == "PATCH"):
        if (Customers.objects.get(user_id = request.user.id).custLevel != 1):
            return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        try:
            category_info = Category.objects.filter(id = category_id)
            category_info_values = category_info.get()
        except:
            return HttpResponse("category does not exist", status = status.HTTP_404_NOT_FOUND)
        try:
            # get the data and check if the data is valid
            data = json.loads(request.body.decode('utf-8'))
            if ('name' in data.keys()):
                category_info_values.name = data['name']
            if ('description' in data.keys()):
                category_info_values.description = data['description']
            if ('image' in data.keys()):
                category_info_values.image = data['image']
        except:
            return HttpResponse('Json Decode Error', status=status.HTTP_400_BAD_REQUEST)
        try:
            # update the data
            category_info_values.save()
            updated_category_info = list(category_info.values())
            return JsonResponse(updated_category_info, safe=False, status = status.HTTP_201_CREATED, 
                                        content_type = 'application/json')
        except:
            return HttpResponse('Update failed', status=status.HTTP_400_BAD_REQUEST)
    elif (request.method == "DELETE"):
        if (Customers.objects.get(user_id = request.user.id).custLevel != 1):
            return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        category = Category.objects.filter(id = category_id)
        # if category exists it delte the category
        if (category.exists()):
            category.delete()
            return HttpResponse('The data is successfully deleted', status = status.HTTP_200_OK)
        else:
            return HttpResponse("category does not exist", status = status.HTTP_404_NOT_FOUND)
    else:
        return HttpResponse('Unavailable Request', status = status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def Discount_view(request):
    """ This view is an API for the discounts"""
    if (request.method == "GET"):
        all_discounts = list(Discount.objects.all().values())
        return JsonResponse(all_discounts, safe=False, status=status.HTTP_200_OK)
    elif (request.method == "POST"):
        if (Customers.objects.get(user_id = request.user.id).custLevel != 1):
            return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        try:
            # get the data and check if the data is valid
            data = json.loads(request.body.decode('utf-8'))
            if (data['minQuan'] > data['maxQuan']):
                HttpResponse("minQuan cannot be larger than maxQuan", safe=False, status = status.HTTP_404_NOT_FOUND)
            new_discount = Discount(percentage = data['percentage'],
                                    minQuan = data['minQuan'],
                                    maxQuan = data['maxQuan'],
                                    disShipping = data['disShipping'])
        except:
            return HttpResponse('Json Decode Error', status=status.HTTP_400_BAD_REQUEST)
        try:
            new_discount.save()
        except:
            return HttpResponse("could not save into the database", status = status.HTTP_404_NOT_FOUND)
        return JsonResponse(data, safe=False, status=status.HTTP_201_CREATED, 
                                        content_type='application/json')
    elif (request.method == "PATCH"):
        if (Customers.objects.get(user_id = request.user.id).custLevel != 1):
            return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        try:
            data = json.loads(request.body.decode('utf-8'))
            discount = Discount.objects.get(id = data['id'])
            # if the key exists it updates the data
            if ('percentage' in data.keys()):
                discount.percentage = data['percentage']
            if ('minQuan' in data.keys()):
                discount.minQuan = data['minQuan']
            if ('maxQuan' in data.keys()):
                discount.maxQuan = data['maxQuan']
            if ('disShipping' in data.keys()):
                discount.disShipping = data['disShipping']
            if (discount.minQuan > discount.maxQuan):
                return HttpResponse('minQuan cannot be larger than maxQuan', status=status.HTTP_400_BAD_REQUEST)
            try:
                discount.save()
            except:
                HttpResponse('Updating failed', status=status.HTTP_400_BAD_REQUEST)
            new_discount = list(Discount.objects.all().values().filter(id = data['id']))
            return JsonResponse(new_discount, safe=False, status=status.HTTP_201_CREATED, 
                                        content_type='application/json')
        except:
            return HttpResponse('Json Decode Error', status=status.HTTP_400_BAD_REQUEST)
    else:
        return HttpResponse('Unavailable Request', status = status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def Product_view(request):
    """ THis view is an API for products"""
    if (request.method == "GET"):
        all_products = list(Products.objects.all().values())
        # change the category id to category
        for product in all_products:
            product['category'] = list(Category.objects.all().values().filter(id = product['category_id']))
        return JsonResponse(all_products, safe=False, status=status.HTTP_200_OK)
    elif (request.method == "POST"):
        if (Customers.objects.get(user_id = request.user.id).custLevel != 1):
            return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        try:
            # check if the data is valid
            data = json.loads(request.body.decode('utf-8'))
            if ('description' not in data.keys()):
                data['description'] = ""
            if ('image' not in data.keys()):
                data['image'] = None
            try:
                # connecting foerign key with Category
                category = Category.objects.all().filter(name = data['category'])[0]
            except:
                return HttpResponse('Check category name', 
                        status=status.HTTP_400_BAD_REQUEST)
            new_product = Products(name = data['name'],
                                    description = data['description'],
                                    image = data['image'],
                                    price = data['price'],
                                    category = category,
                                    max_quantity = data['max_quantity'],
                                    min_quantity_retail = data['min_quantity_retail'])
            new_product.save()
            discount_list = []
            # connects many-to-many relationship with discounts
            for discount in data['discount']:
                new_product.discount.add(Discount.objects.get(id=discount))
                discount_list.append(Discount.objects.all().values().filter(id=discount)[0])
        except:
            return HttpResponse('json encoding failed', 
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            new_product.save()
        except:
            return HttpResponse('could not save to the database', 
                        status=status.HTTP_400_BAD_REQUEST)
        post_product = {
            'name':data['name'],
            'description':data['description'],
            'image':data['image'],
            'price':data['price'],
            'category': Category.objects.all().values().filter(name = data['category'])[0],
            'max_quantity':data['max_quantity'],
            'min_quantity_retail':data['min_quantity_retail'],
            'discounts':discount_list
        }
        return JsonResponse(post_product, safe=False, status=status.HTTP_200_OK)
    elif (request.method == "DELETE"):
        if (Customers.objects.get(user_id = request.user.id).custLevel != 1):
            return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        try:
            data = json.loads(request.body.decode('utf-8'))
            product_name = data['name']
        except:
            return HttpResponse('Json encode error', status = status.HTTP_400_BAD_REQUEST)
        try:
            product_info = Products.objects.get(name = product_name)
        except:
            return HttpResponse('product does not exist', status = status.HTTP_404_NOT_FOUND)
        try:
            product_info.delete()
        except:
            return(HttpResponse('The user does not exist',
                                 status = status.HTTP_404_NOT_FOUND))
        return HttpResponse('The data is successfully deleted', status = status.HTTP_200_OK)
    else:
        return HttpResponse('Unavailable Request', status = status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def Product_detail_view(request, product_id):
    """ This view is an API of the product detail"""
    if (request.method == "GET"):
        try:
            product_detail = list(Products.objects.all().values().filter(id = product_id))[0]
        except:
            return HttpResponse("product does not exist", status = status.HTTP_404_NOT_FOUND)
        try:
            product_detail['category'] = list(Category.objects.all().values().filter(id = product_detail['category_id']))[0]
        except:
            return HttpResponse('category does not exists', status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(product_detail, safe=False, status = status.HTTP_200_OK, 
                                content_type = 'application/json')
    elif (request.method == "PATCH"):
        if (Customers.objects.get(user_id = request.user.id).custLevel != 1):
            return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        try:
            product_detail = Products.objects.filter(id = product_id)
            product_detail_info = product_detail.get()
        except:
            return HttpResponse('product does not exists', status=status.HTTP_400_BAD_REQUEST)
        try:
            data = json.loads(request.body.decode('utf-8'))
            if ('name' in data.keys()):
                product_detail_info.name = data['name']
            if ('description' in data.keys()):
                product_detail_info.description = data['description']
            if ('price' in data.keys()):
                product_detail_info.price = data['price']
            if ('category' in data.keys()):
                product_detail_info.category = Category.objects.all().filter(name = data['category'])[0]
            if ('image' in data.keys()):
                product_detail_info.image = data['image']
            if ('max_quantity' in data.keys()):
                product_detail_info.max_quantity = data['max_quantity']
            if ('min_quantity_retail' in data.keys()):
                product_detail_info.min_quantity_retail = data['min_quantity_retail']
            discount_list = []
            if ('discount' in data.keys()):
                product_detail_info.discount.clear()
                try:
                    for discount in data['discount']:
                        product_detail_info.discount.add(Discount.objects.get(id=discount))
                        discount_list.append(Discount.objects.all().values().filter(id=discount)[0])
                except:
                    return HttpResponse('Could not find discount', status=status.HTTP_400_BAD_REQUEST)
            product_detail_info.save()
            updated_product = Products.objects.all().values().filter(id=product_id)[0]
            updated_product['category'] = Category.objects.all().values().filter(name = data['category'])[0]
            updated_product['discounts'] = discount_list
            return JsonResponse(updated_product, safe=False, status = status.HTTP_201_CREATED, 
                                        content_type = 'application/json')
        except:
            return HttpResponse('Json Decode Error', status=status.HTTP_400_BAD_REQUEST)
    else:
        return HttpResponse('Unavailable Request', status = status.HTTP_400_BAD_REQUEST)
