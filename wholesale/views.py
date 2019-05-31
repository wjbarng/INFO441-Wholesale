from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .forms import RegistrationForm, ShippingAddressForm, ProductRegistrationForm, BusinessApplicationForm
from django.contrib.auth.models import User
from wholesale.models import Customers, Cart, Payment, ShippingAddress, BusinessApplication, Category, Discount, ShippingMethod, Products, Prod_dis, Order
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from decimal import Decimal
from django.db import DatabaseError
import json
import datetime

""" Web scraping """
from bs4 import BeautifulSoup
import requests


DatabaseErrorMessage = "Error interacting with database."
""" web page to scrape from """
page = 'https://www.directliquidation.com/liquidation-102/top-5-benefits-buying-wholesale-merchandise-discounted-retailer-business/'

@csrf_exempt
def homepage(request):
    page_response = requests.get(page, timeout=5)
    page_content = BeautifulSoup(page_response.content, "html.parser")
    return render(request, "index.html", {'title1': page_content.find_all("h2")[0].get_text(), 'content1': page_content.find_all("p")[1].get_text(), 
                                          'title2': page_content.find_all("h2")[1].get_text(), 'content2': page_content.find_all("p")[5].get_text(),
                                          'title3': page_content.find_all("h2")[2].get_text(), 'content3': page_content.find_all("p")[7].get_text(),
                                          'title4': page_content.find_all("h2")[3].get_text(), 'content4': page_content.find_all("p")[11].get_text(),
                                          'title5': page_content.find_all("h2")[4].get_text(), 'content5': page_content.find_all("p")[12].get_text() })


@csrf_exempt
def default_category():
    categories = {
        'Pantry & Dry Goods':"images/peanut_butter.jpg",
        'Bath & Facial Tissue':"images/tissue.jpg",
        'Canned Goods':"images/canned_good.jpeg",
        'Cleaning Products':"images/dish_detergent.jpg",
        'Coffee & Sweeteners':"images/coffee.jpg",
        'Emergency Kits & Supplies':"images/mountain_house.jpg",
        'Breakroom Serving Supplies':"images/break_room.jpg",
        'Gourmet Foods':"images/cheese.jpg",
        'Paper Towels':"images/paper_towel.jpg",
        'Snacks':"images/snacks.jpg",
        'Water & Beverages':"images/water.jpg"
    }
    # Category.objects.all().delete()
    exist_category = [one['name'] for one in list(Category.objects.all().values())]
    for category, image in categories.items():
        if (category not in exist_category):
            new_category = Category(name=category, image=image)
            new_category.save()
    print(Category.objects.all().values())
    print(Cart.objects.all())
default_category()

@csrf_exempt
def default_shipping():
    if not ShippingMethod.objects.filter(ShipMethName = 'Two day'):
        one = ShippingMethod(ShipMethName = 'Two day', ShipMethDesc = "two day shipping", ShipMethPrice = 10.0)
        one.save()
        two = ShippingMethod(ShipMethName = 'Four day', ShipMethDesc = "Four day shipping", ShipMethPrice = 6.0)
        two.save()
        three = ShippingMethod(ShipMethName = 'Seven day', ShipMethDesc = "Seven day shipping", ShipMethPrice = 4.0)
        three.save()
default_shipping()

@csrf_exempt
def products(request, category_id):
    if (request.method == "GET"):
        products = Products.objects.all().filter(category = category_id)
        # return render(request, "products.html", {'products':products})
        return render(request,'products.html', {'products':products})

@csrf_exempt
def categories(request):
     if (request.method == "GET"):
        categories = Category.objects.all()
        print(categories)
        return render(request,'category.html', {'categories':categories})

@csrf_exempt
def product_detail(request, product_id, category_id):
    """ This is a view page for the product detail """
    print("product_detail")
    print(request.method)
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
    elif (request.method == "POST"):
        print("post")
        try:
            product = Products.objects.all().filter(id = product_id).values()[0]
        except:
            return HttpResponse("Product does not exists.", status=404)
        try:
            category = Category.objects.all().filter(id = product['category_id']).values()[0]
        except:
            return HttpResponse("Category does not exists.", status=404)
        print(Cart.objects.all())
        print(type(request.POST['quantity']))
        # cart_item = Cart.objects.all().filter(customer_id = )
        print(request.user.id)
        u = User.objects.get(id = request.user.id)
        customer = u.customers
        print("test1")
        product = Products.objects.all().filter(id = product_id)[0]
        print(Cart.objects.all().filter(customer=customer, prodName=product))
        print("test2")
        if (len(Cart.objects.all().filter(customer=customer, prodName=product)) != 0):
            try:
                print("test")
                cart_info = Cart.objects.filter(customer=customer, prodName=product).values()[0]
                cart_info_values = Cart.objects.get(customer=customer, prodName=product)
                print(cart_info)
            except:
                messages.error(request,('item does not exist'))
                HttpResponseRedirect('product detail')
            try:
                # update the data
                print("test13")
                print(type(cart_info['prodQuantity']))
                print("test15")
                cart_info_values.prodQuantity = cart_info['prodQuantity'] + int(request.POST['quantity'])
                print(cart_info['prodQuantity'] + int(request.POST['quantity']))
                print("test16")
                cart_info_values.save()
            except:
                messages.error(request,('could not update the quantity'))
                HttpResponseRedirect('product detail')
        else:
            new_item = Cart(customer=customer, prodName=product, prodQuantity=request.POST['quantity'])
            new_item.save()
        print(Cart.objects.all().values())
        return HttpResponse(render(request, "productDetail.html", 
			{'product':product, 'category':category}), status=200)
    else:
        return HttpResponse("Method not allowed on /product/id.", status=405)

@csrf_exempt
def product_regi(request):
    """ This is a view page for the product registraion """
    if (request.method == "POST"):
        try:
            if (not request.user.is_authenticated or 
                Customers.objects.get(user_id = request.user.id).custLevel != 3):
                return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        except:
            return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        form = ProductRegistrationForm(request.POST)
        if form.is_valid():
            clean_data = form.clean()
            # try:
            try:
                # connecting foerign key with Category
                # Category.objects.all().delete()
                category = Category.objects.all().filter(name = clean_data['category'])[0]
                print(category)
                # if(not category.exists()):
                #     print("test1")
                #     Category(name = clean_data['category'], image=None).save()
                #     print(Category.objects.all().values())
                #     category = Category.objects.all().filter(name = clean_data['category'])
                #     print(category)
                # print("test2")
            except:
                return HttpResponse('Check category name', 
                    status=status.HTTP_400_BAD_REQUEST)
            print(category)
            new_product = Products(name = clean_data['name'],
                                description = clean_data['description'],
                                image = clean_data['image'],
                                price = clean_data['price'],
                                category = category,
                                max_quantity = clean_data['max_quantity'],
                                min_quantity_retail = clean_data['min_quantity_retail'])
            new_product.save()
            print("success")
            # add discount
            messages.success(request,('You have successfully registered'))
            return render(request, "products.html")
            # except:
            #     messages.error(request,('Could not register product'))
            #     return render(request, "products.html")
        else:
            messages.error(request,('Form not valid'))
            HttpResponseRedirect('registerProduct')
    elif request.method == "DELETE":
        if request.user.is_authenticated:
            User.objects.filter(id = request.user.id).delete()
            Customers.objects.filter(user = request.user).delete()
    elif request.method == "GET":
        return render(request, "registerProduct.html", {'form': ProductRegistrationForm})

@csrf_exempt
def cart(request):
    if request.user.is_authenticated:
        u = User.objects.get(id = request.user.id)
        user = User.objects.get(username=u)
        customer = user.customers
        address = ShippingAddress.objects.filter(custID=customer)
        paymentid = Customers.objects.values_list('PaymentID', flat = True).filter(user = request.user)
        if paymentid[0] is not None:
            number = Payment.objects.values_list('CardNumber', flat = True).get(id=list(paymentid)[0])
            name = Payment.objects.values_list('Name', flat = True).get(id=list(paymentid)[0])
        else:
            number = 'Please set a credit card number'
            name = 'Please set a credit card name'
        products = Cart.objects.filter(customer=customer)
        cartList = []
        total = 0
        for prod in products:
            productPrice = Products.objects.values_list('price', flat = True).get(name = prod.prodName.name)
            obj = {'name': prod.prodName.name, 'price': productPrice, 'quantity': prod.prodQuantity}
            cartList.append(obj)
            total += productPrice * prod.prodQuantity

        if request.method == 'GET':
            return render(request, "cart.html", {'ship': address, 'number': number, 'name': name, 'product': cartList, 'total': total})
        elif request.method == 'POST':
            shippingPrice = request.POST['optradio']
            shippingMethod = ShippingMethod.objects.get(ShipMethPrice = shippingPrice)
            totalPrice = float(total) + float(shippingPrice)
            payment = Payment.objects.get(id=list(paymentid)[0])
            order = Order.objects.create(customer = customer, orderDate = datetime.date.today(), shippedDate = datetime.date.today(),
                                         totalPrice = totalPrice, payment = payment, shippingAddress = ShippingAddress.objects.get(custID=customer), shippingMethod = shippingMethod)
            order.save()
            Cart.objects.filter(customer=customer).delete()
            messages.success(request,('Your order has been processed!'))
            cartList = []
            return render(request, 'cart.html', {'ship': address, 'number': number, 'name': name, 'product': cartList})
    else:
        return HttpResponse(status = status.HTTP_403_FORBIDDEN)

@csrf_exempt
def about(request):
    return render(request, "about.html", {})

@csrf_exempt
def support(request):
    return render(request, "support.html", {})

     

""" Post a new business application or delete an application by business name """
""" Stanley worked on this function, app did not work when I removed this function"""
@csrf_exempt
def application(request):
    if request.method == 'GET':
        return render(request, 'application.html', {'form': BusinessApplicationForm})
    elif request.method == 'POST':
        form = BusinessApplicationForm(request.POST)
        if form.is_valid():
            try:
                application = BusinessApplication.objects.create(busName = form.cleaned_data['busName'], busAddress = form.cleaned_data['busAddress'], 
                                                                busZip = form.cleaned_data['busZip'], busCity = form.cleaned_data['busCity'], 
                                                                busState = form.cleaned_data['busState'], busEmail = form.cleaned_data['busEmail'], 
                                                                busPhone = form.cleaned_data['busPhone'])
                application.save()
            except DatabaseError:
                return HttpReponse(DatabaseErrorMessage, status=400)
            messages.success(request,('Application submitted'))
            return redirect('home')
        else:
            messages.error(request,('Application form not valid'))
            return redirect('application')
    elif request.method == 'DELETE':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except:
            return HttpResponse('Json encode error', status = status.HTTP_400_BAD_REQUEST)
        application = BusinessApplication.objects.filter(busName = data['name'])
        if application.exists():
            application.delete()
            return HttpResponse("Delete successful", status = status.HTTP_200_OK)
        else:
            return HttpResponse("Application not found", status = status.HTTP_404_NOT_FOUND)
    else:
        return HttpResponse('Unavailable Request', status = status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def account(request):
    if request.method == 'GET':
        u = User.objects.get(id = request.user.id)
        user = User.objects.get(username=u)
        customer = user.customers
        return render(request, 'account/account.html', {'customer': customer})
    """ Update and create new account information """
    # elif request.method == 'PATCH':
    #     if request.user.is_authenticated:
    #         """ Update password for user """
    #         try:
    #             data = json.loads(request.body.decode('utf-8'))
    #         except:
    #             return HttpResponse('Json encode error', status = status.HTTP_400_BAD_REQUEST)
    #         u = User.objects.get(id = request.user.id)
    #         u.password = data['password']
    #         u.save()
    #         messages.success(request,('Password updated'))
    #         return redirect('account')
    #     else:
    #         return HttpResponse(status = status.HTTP_403_FORBIDDEN)

""" Creates new address for shipping or deletes address associated with user """
""" Stanley worked on this function, App does not work without this function"""
@csrf_exempt
def shipping(request):
    if request.user.is_authenticated:
        u = User.objects.get(id = request.user.id)
        customer = u.customers
        if request.method == 'GET':
            address = ShippingAddress.objects.filter(custID=customer)
            return render(request, 'account/shipping.html', {"ship": address, "customer": customer})
        elif request.method == "POST":
            if customer.custLevel == 1:
                first = request.POST['firstName']
                last = request.POST['lastName']
            else:
                business = request.POST['businessName']
            address = request.POST['address']
            city = request.POST['city']
            state = request.POST['state']
            shipZip = request.POST['zip']
            number = request.POST['number']
            try:
                if ShippingAddress.objects.filter(custID=customer).count():
                    ShippingAddress.objects.filter(custID=customer).delete()
                if customer.custLevel == 1:
                    shippingAddress = ShippingAddress.objects.create(custID=customer, shipAddFname = first,
                                        shipAddLname = last, shipAddAddress = address, shipAddCity = city,
                                        shipAddState = state, shipAddZip = shipZip, shipAddPhone = number)
                else:
                     shippingAddress = ShippingAddress.objects.create(custID=customer, businessName = business, 
                                                                      shipAddAddress = address, shipAddCity = city,
                                                                      shipAddState = state, shipAddZip = shipZip, shipAddPhone = number)
                shippingAddress.save()
                print(ShippingAddress.objects.all().values())
            except DatabaseError:
                return HttpReponse(DatabaseErrorMessage, status=400)
            messages.success(request,('Address saved'))
            address = ShippingAddress.objects.filter(custID_id=customer)
            print(address)
            return render(request, "account/shipping.html", {"ship": address, "customer": customer})
        elif request.method == "DELETE":
            if request.user.is_authenticated:
                u = User.objects.get(id = request.user.id)
                customer = u.customers
                shippingAddress = ShippingAddress.objects.filter(custID = customer)
                if shippingAddress.exists():
                    shippingAddress.delete()
                    return HttpResponse("Delete successful", status = status.HTTP_200_OK)
                else:
                    return HttpResponse("Addresses not found", status = status.HTTP_404_NOT_FOUND)
            else:
                return HttpResponse(status = status.HTTP_403_FORBIDDEN)
        else:
            return HttpResponse('Unavailable Request', status = status.HTTP_400_BAD_REQUEST)
    else:
        return HttpResponse(status = status.HTTP_403_FORBIDDEN)

@csrf_exempt
def payment(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            paymentid = Customers.objects.values_list('PaymentID', flat = True).filter(user = request.user)
            if paymentid[0] is not None:
                number = Payment.objects.values_list('CardNumber', flat = True).get(id=list(paymentid)[0])
                name = Payment.objects.values_list('Name', flat = True).get(id=list(paymentid)[0])
            else:
                number = 'Please set a credit card number'
                name = 'Please set a credit card name'
            return render(request, "account/payment.html", {'number': number, 'name': name})
        elif request.method == 'POST':
            number = request.POST['cardNumber']
            name = request.POST['name']
            try:
                """ Create new card entry """
                payment = Payment.objects.create(CardNumber = number, Name = name)
                payment.save()
                paymentid = Customers.objects.values_list('PaymentID', flat = True).filter(id = request.user.id)
                if paymentid.exists():
                    Payment.objects.filter(id = paymentid).delete()
            except DatabaseError:
                return HttpResponse(DatabaseErrorMessage, status=400)
            """ Update customer table with new payment """
            u = User.objects.get(id = request.user.id)
            user = User.objects.get(username=u)
            customer = user.customers
            customer.PaymentID = payment
            customer.save()
            messages.success(request,('Card saved'))
            return render(request, "account/payment.html", {'number': number, 'name': name})
        else:
            return HttpResponse('Unavailable Request', status = status.HTTP_400_BAD_REQUEST)
    else:
        return HttpResponse(status = status.HTTP_403_FORBIDDEN)

@csrf_exempt
def order(request):
    if request.user.is_authenticated:
        u = User.objects.get(id = request.user.id)
        customer = u.customers
        order = Order.objects.filter(customer=customer)
        return render(request, "account/order.html", {'order': order})
    else:
        return HttpResponse(status = status.HTTP_403_FORBIDDEN)

""" Sign user in on post, update password on patch, or get sign in 
    form on get """
""" Stanley worked on this function"""
@csrf_exempt
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
""" Stanley worked on this function"""
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
            elif User.objects.filter(username=form.cleaned_data['username']).exists():
                messages.error(request,('Username has been taken'))
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
    """ This view is an API for the categories, see readme for documentation"""
    if (request.method == "GET"):
        all_category = list(Category.objects.all().values())
        return JsonResponse(all_category, safe=False, status=status.HTTP_200_OK)
    elif (request.method == "POST"):
        try:
            if (not request.user.is_authenticated or 
                Customers.objects.get(user_id = request.user.id).custLevel != 1):
                return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        except:
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
    """ This view is an API for the category detail, see readme for more information"""
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
        try:
            if (not request.user.is_authenticated or 
                Customers.objects.get(user_id = request.user.id).custLevel != 1):
                return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        except:
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
            # if ('description' in data.keys()):
            #     category_info_values.description = data['description']
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
        try:
            if (not request.user.is_authenticated or 
                Customers.objects.get(user_id = request.user.id).custLevel != 1):
                return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        except:
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
    """ This view is an API for the discounts, see readme for more information"""
    if (request.method == "GET"):
        all_discounts = list(Discount.objects.all().values())
        return JsonResponse(all_discounts, safe=False, status=status.HTTP_200_OK)
    elif (request.method == "POST"):
        try:
            if (not request.user.is_authenticated or 
                Customers.objects.get(user_id = request.user.id).custLevel != 3):
                return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        except:
            return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        try:
            # get the data and check if the data is valid
            data = json.loads(request.body.decode('utf-8'))
            if (data['minQuan'] > data['maxQuan']):
                HttpResponse("minQuan cannot be larger than maxQuan", 
                            safe=False, status = status.HTTP_404_NOT_FOUND)
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
        try:
            if (not request.user.is_authenticated or 
                Customers.objects.get(user_id = request.user.id).custLevel != 1):
                return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        except:
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
                return HttpResponse('minQuan cannot be larger than maxQuan', 
                        status=status.HTTP_400_BAD_REQUEST)
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
    """ THis view is an API for products, see documentation for more detail"""
    if (request.method == "GET"):
        all_products = list(Products.objects.all().values())
        print(all_products)
        # change the category id to category
        for product in all_products:
            product['category'] = list(Category.objects.all().values().filter(id = product['category_id']))
        return JsonResponse(all_products, safe=False, status=status.HTTP_200_OK)
    elif (request.method == "POST"):
        try:
            if (not request.user.is_authenticated or 
                Customers.objects.get(user_id = request.user.id).custLevel != 1):
                return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        except:
            return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        try:
            print("hieel")
            # check if the data is valid
            data = json.loads(request.body.decode('utf-8'))
            if ('description' not in data.keys()):
                data['description'] = ""
            if ('image' not in data.keys()):
                data['image'] = ""
            try:
                # connecting foerign key with Category
                category = Category.objects.all().filter(name = data['category'])[0]
            except:
                return HttpResponse('Check category name', 
                        status=status.HTTP_400_BAD_REQUEST)
            print("hihi")
            new_product = Products(name = data['name'],
                                    description = data['description'],
                                    image = data['image'],
                                    price = data['price'],
                                    category = category,
                                    max_quantity = data['max_quantity'],
                                    min_quantity_retail = data['min_quantity_retail'])
            new_product.save()
            print("hi")
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
        try:
            if (not request.user.is_authenticated or 
                Customers.objects.get(user_id = request.user.id).custLevel != 1):
                return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        except:
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
        try:
            if (not request.user.is_authenticated or 
                Customers.objects.get(user_id = request.user.id).custLevel != 1):
                return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        except:
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
            updated_product['category'] = Category.objects.all().values().filter(id = updated_product['category_id'])[0]
            updated_product['discounts'] = discount_list
            return JsonResponse(updated_product, safe=False, status = status.HTTP_201_CREATED, 
                                        content_type = 'application/json')
        except:
            return HttpResponse('Json Decode Error', status=status.HTTP_400_BAD_REQUEST)
    else:
        return HttpResponse('Unavailable Request', status = status.HTTP_400_BAD_REQUEST)
