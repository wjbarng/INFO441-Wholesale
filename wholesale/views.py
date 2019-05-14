from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .forms import RegistrationForm, ShippingAddressForm
from django.contrib.auth.models import User
from wholesale.models import Customers, Payment, ShippingAddress
from .models import Category, Discount, ShippingMethod, Products, Prod_dis, Order, Prod_order
from django.contrib.auth import authenticate, login, logout

# Create your views here.
from rest_framework import viewsets

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User

import json
import datetime

def homepage(request):
	return render(request, "index.html", {})

def products(request):
    return render(request, "products.html", {})

def wholesale(request):
    return render(request, "wholesale.html", {})

def about(request):
    return render(request, "about.html", {})

def support(request):
    return render(request, "support.html", {})

def shipping(request):
    if request.method == 'GET':
        return render(request, 'account.html', {'shippingForm': ShippingAddressForm})
    elif request.method == "POST":
        if request.user.is_authenticated:
            form = ShippingAddressForm(request.POST)
            if form.is_valid():
                u = User.objects.get(id = request.user.id)
                customer = u.customers
                shippingAddress = ShippingAddress.objects.create(custID=customer, shipAddFname = form.cleaned_data['first_name'],
                                    shipAddLname = form.cleaned_data['last_name'], shipAddAddress = form.cleaned_data['address'], shipAddCity = form.cleaned_data['city'],
                                    shipAddState = form.cleaned_data['state'], shipAddZip = form.cleaned_data['shipZip'], shipAddPhone = form.cleaned_data['phone'])
                shippingAddress.save()
                messages.success(request,('Address saved'))
                return render(request, "account.html", {'address': form.cleaned_data['address']})
            else:
                messages.error(request,('Address form not valid'))
                return redirect('account')

    

""" Update and create new account information """
def account(request):
    if request.method == 'PATCH':
        if request.user.is_authenticated:
            """ Update password for user """
            newPassword = request.POST['editPassword']
            u = User.objects.get(id = request.user.id)
            u.password = newPassword
            u.save()
            messages.success(request,('Password updated'))
            return redirect('account')
    elif request.method == 'GET':
        return render(request, "account.html", {'shippingForm': ShippingAddressForm})
    elif request.method == 'POST':
        if request.user.is_authenticated:
            number = request.POST['cardNumber']
            name = request.POST['name']
            payment = Payment.objects.create(CardNumber = number, Name = name)
            payment.save()
            """ Update customer table with new payment """
            u = User.objects.get(id = request.user.id)
            customer = u.customers
            customer.PaymentId = payment
            customer.save()

            messages.success(request,('Card saved'))
            return render(request, "account.html", {'number': number, 'name': name, 'shippingForm': ShippingAddressForm})

""" Sign user in on post, update password on patch, or get sign in 
    form on get """
def signin(request):
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


def signout(request):
    logout(request)
    messages.success(request,('You have been logged out'))
    return redirect('home')			




@csrf_exempt
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
                custState = form.cleaned_data['custState'], custPhone = form.cleaned_data['custPhone'])
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
    elif request.method == "GET":
        return render(request, "register.html", {'form': RegistrationForm})

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
                data['image'] = None
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
def Category_detail_view(request, category_id):
    if (request.method == "GET"):
        try:
            category_info = Category.objects.all().values().get(id = category_id)
        except:
            return HttpResponse("category does not exist", status = status.HTTP_404_NOT_FOUND)
        return JsonResponse(category_info, safe=False, status = status.HTTP_200_OK, 
                                content_type = 'application/json')
    elif (request.method == "PATCH"):
        try:
            category_info = Category.objects.filter(id = category_id)
            category_info_values = category_info.get()
        except:
            return HttpResponse("category does not exist", status = status.HTTP_404_NOT_FOUND)
        try:
            data = json.loads(request.body.decode('utf-8'))
            if ('name' in data.keys()):
                category_info_values.name = data['name']
            if ('description' in data.keys()):
                category_info_values.description = data['description']
            if ('name' in data.keys()):
                category_info_values.image = data['image']
        except:
            return HttpResponse('Json Decode Error', status=status.HTTP_400_BAD_REQUEST)
        try:
            category_info_values.save()
            updated_category_info = list(category_info.values())
            return JsonResponse(updated_category_info, safe=False, status = status.HTTP_201_CREATED, 
                                        content_type = 'application/json')
        except:
            return HttpResponse('Update failed', status=status.HTTP_400_BAD_REQUEST)
    elif (request.method == "DELETE"):
        category = Category.objects.filter(id = category_id)
        if (category.exists()):
            category.delete()
            return HttpResponse('The data is successfully deleted', status = status.HTTP_200_OK)
        else:
            return HttpResponse("category does not exist", status = status.HTTP_404_NOT_FOUND)
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
            print(data)
            if (data['minQuan'] >= data['maxQuan']):
                HttpResponse("minQuan cannot be larger than maxQuan", safe=False, status = status.HTTP_404_NOT_FOUND)
            print(data)
            new_discount = Discount(
                percentage = data['percentage'],
                minQuan = data['minQuan'],
                maxQuan = data['maxQuan'],
                disShipping = data['disShipping']
            )
        except:
            return HttpResponse('Json Decode Error', status=status.HTTP_400_BAD_REQUEST)
        try:
            new_discount.save()
        except:
            return HttpResponse("could not save into the database", status = status.HTTP_404_NOT_FOUND)
        return JsonResponse(data, safe=False, status=status.HTTP_201_CREATED, 
                                        content_type='application/json')
    else:
        return HttpResponse('Unavailable Request', status = status.HTTP_400_BAD_REQUEST)


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
                'name':data['name'],
                'description':data['description'],
                'image':data['image'],
                'price':data['price'],
                'category':data['category'],
                'max_quantity':data['max_quantity'],
                'min_quantity':data['min_quantity']
            }
            return JsonResponse(post_product, safe=False, status=status.HTTP_200_OK)
        except:
            return HttpResponse('json encoding failed', 
                            status=status.HTTP_400_BAD_REQUEST)
    elif (request.method == "DELETE"):
        try:
            data = json.loads(request.body.decode('utf-8'))
            product_id = data['id']
        except:
            return HttpResponse('Json encode error', status = status.HTTP_400_BAD_REQUEST)
        try:
            product_info = Products.objects.filter(id = product_id)
            product_info_value = product_info.get()
        except:
            return HttpResponse('prodcut does not exist', status = status.HTTP_404_NOT_FOUND)
        try:
            user_channel_info_value.delete()
        except:
            return(HttpResponse('The user does not exist', safe=False,
                                 status = status.HTTP_404_NOT_FOUND))
        return HttpResponse('The data is successfully deleted', status = status.HTTP_200_OK)
    else:
        return HttpResponse('Unavailable Request', status = status.HTTP_400_BAD_REQUEST)

def Product_detail_view(request, product_id):
    if (request.method == "GET"):
        try:
            product_detail = list(Products.objects.all().values().filter(id = product_id))
        except:
            return HttpResponse("product does not exist", status = status.HTTP_404_NOT_FOUND)
        return JsonResponse(product_detail, safe=False, status = status.HTTP_200_OK, 
                                content_type = 'application/json')
    elif (request.method == "PATCH"):
        try:
            product_detail = Products.objects.get(id = product_id)
            product_detail_value = product_detail.get()
        except:
            return HttpResponse('product does not exists', status=status.HTTP_400_BAD_REQUEST)
        try:
            data = json.loads(request.body.decode('utf-8'))
            for key in data.keys():
                product_detail_value[key] = data[key]
            return JsonResponse(list(product_detail.values)[0], safe=False, status = status.HTTP_201_CREATED, 
                                        content_type = 'application/json')
        except:
            return HttpResponse('Json Decode Error', status=status.HTTP_400_BAD_REQUEST)
    else:
        return HttpResponse('Unavailable Request', status = status.HTTP_400_BAD_REQUEST)
