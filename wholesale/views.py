from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .forms import RegistrationForm, ShippingAddressForm, ProductRegistrationForm, BusinessApplicationForm
from django.contrib.auth.models import User
from wholesale.models import Customers, Cart, Payment, ShippingAddress, BusinessApplication, Category, Discount, ShippingMethod, Products, Order
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout 
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from django.http import JsonResponse, HttpResponse
from decimal import Decimal
from django.db import DatabaseError
import json
import datetime
from django.views.decorators.debug import sensitive_post_parameters

""" Web scraping """
from bs4 import BeautifulSoup
import requests


DatabaseErrorMessage = "Error interacting with database."
""" web pages to scrape from """
page = 'https://www.directliquidation.com/liquidation-102/top-5-benefits-buying-wholesale-merchandise-discounted-retailer-business/'
walmart = 'https://www.walmart.com/tp/peanut-butter'

""" Scrapes information on product and inserted into Products table """
@csrf_exempt
def web_scraping():
    page_response = requests.get(walmart, timeout=10)
    page_content = BeautifulSoup(page_response.content, "html.parser")
    productName = page_content.find_all("h2")[0].get_text()
    productUrl = page_content.findAll(class_="Tile-img")
    productPrice = page_content.findAll("span", class_='Price-group')
    category = Category.objects.get(name='Pantry & Dry Goods')
    if not Products.objects.filter(name=productName):
        new_product = Products(name = productName,
                        description = "Creamy Peanut Butter",
                        image = productUrl[0]['src'],
                        price = float(productPrice[0]['title'][1:]),
                        category = category,
                        max_quantity = 100,
                        min_quantity_retail = 10)
        new_product.save()
web_scraping()

@csrf_exempt
def homepage(request):
    # page_response = requests.get(page, timeout=100)
    # page_content = BeautifulSoup(page_response.content, "html.parser")
    return render(request, "index.html", {}, status=status.HTTP_200_OK)

""" Inserts all categories into Category table if they have not been inserted """
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
    exist_category = [one['name'] for one in list(Category.objects.all().values())]
    for category, image in categories.items():
        if (category not in exist_category):
            new_category = Category(name=category, image=image)
            new_category.save()
default_category()

""" Inserts all shipping methods into ShippingMethod table if they have not been inserted """
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
    """ This view renders the products.html"""
    if (request.method == "GET"):
        products = Products.objects.all().filter(category = category_id)
        return render(request,'products.html', {'products':products}, status=status.HTTP_200_OK)

@csrf_exempt
def categories(request):
    """ This view renders the category.html """
    if (request.method == "GET"):
        categories = Category.objects.all()
        return render(request,'category.html', {'categories':categories}, status=status.HTTP_200_OK)

@csrf_exempt
def product_detail(request, product_id, category_id):
    """ This is a view page for the product detail """
    if request.user.is_authenticated:
        u = User.objects.get(id = request.user.id)
        customerLevel = u.customers.custLevel
    else:
        customerLevel = 1

    if (request.method == "GET"):
        try:
            product = Products.objects.all().filter(id = product_id).values()[0]
        except:
            return HttpResponse("Product does not exists.", status=404)
        try:
            category = Category.objects.all().filter(id = product['category_id']).values()[0]
        except:
            return HttpResponse("Category does not exists.", status=404)
        try:
            product_id = Products.objects.all().filter(id = product_id)[0]
            discounts = list(Discount.objects.all().values().filter(product_id=product_id))
        except:
            return HttpResponse("No discounts found", status=404)
        return HttpResponse(render(request, "productDetail.html", 
			{'product':product, 'category':category, 'discounts':discounts, 'customer': customerLevel}), status=status.HTTP_200_OK)
    elif (request.method == "POST"):
        # if the user is signed in, add products into the cart
        if (request.user.is_authenticated):
            try:
                product = Products.objects.all().filter(id = product_id).values()[0]
            except:
                return HttpResponse("Product does not exists.", status=404)
            try:
                category = Category.objects.all().filter(id = product['category_id']).values()[0]
            except:
                return HttpResponse("Category does not exists.", status=404)
            u = User.objects.get(id = request.user.id)
            customer = u.customers
            product = Products.objects.all().filter(id = product_id)[0]
            discounts = list(Discount.objects.all().values().filter(product_id=product_id))
            #if the product is in the cart
            if (len(Cart.objects.all().filter(customer=customer, prodName=product)) != 0):
                try:
                    cart_info = Cart.objects.filter(customer=customer, prodName=product).values()[0]
                    cart_info_values = Cart.objects.get(customer=customer, prodName=product)
                except:
                    messages.error(request,('item does not exist'))
                    HttpResponseRedirect('product detail')
                try:
                    # update the data
                    new_Quantity = cart_info['prodQuantity'] + int(request.POST['quantity'])
                    # Check if new value is over the limit
                    max_quantity = Products.objects.all().values().filter(id = product_id)[0]['max_quantity']
                    discount_max_quan = max_quantity
                    if (len(discounts) != 0):
                        for dis in discounts:
                            discount_max_quan = dis['maxQuan']
                    max_quantity = min(max_quantity, discount_max_quan)
                    if(new_Quantity > max_quantity):
                        messages.error(request,('exceeded quantity limit'))
                        return HttpResponse(render(request, "productDetail.html", 
                            {'product':product, 'category':category, 'discounts':discounts, 'customer': customerLevel}), status=status.HTTP_200_OK)
                    else:
                        cart_info_values.prodQuantity = new_Quantity
                        cart_info_values.save()
                        
                    return HttpResponse(render(request, "productDetail.html", 
                        {'product':product, 'category':category, 'discounts':discounts, 'customer': customerLevel}), status=status.HTTP_200_OK)
                except:
                    messages.error(request,('could not update the quantity'))
                    return HttpResponse(render(request, "productDetail.html", 
                        {'product':product, 'category':category, 'discounts':discounts, 'customer': customerLevel}), status=status.HTTP_200_OK)
            else:
                max_quantity = Products.objects.all().values().filter(id = product_id)[0]['max_quantity']
                discount_max_quan = max_quantity
                if (len(discounts) != 0):
                    for dis in discounts:
                        discount_max_quan = dis['maxQuan']
                max_quantity = min(max_quantity, discount_max_quan)
                if(int(request.POST['quantity']) > max_quantity):
                    messages.error(request,('exceeded quantity limit'))
                    return HttpResponse(render(request, "productDetail.html", 
                        {'product':product, 'category':category, 'discounts':discounts, 'customer': customerLevel}), status=status.HTTP_200_OK)
                else:
                    new_item = Cart(customer=customer, prodName=product, prodQuantity=request.POST['quantity'])
                    new_item.save()
                    messages.success(request,('The item is added to your cart'))
                    return HttpResponse(render(request, "productDetail.html", 
                        {'product':product, 'category':category, 'discounts':discounts, 'customer': customerLevel}), status=status.HTTP_200_OK)
                
        else:
            messages.error(request,('You are not signed in'))
            return redirect(signin)
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
            try:
                # connecting foreign key with Category
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
            try:
                new_product.save()
            except:
                messages.error(request,('product form is not valid'))
                HttpResponseRedirect('registerProduct')
            dis_product = Products.objects.all().filter(name=clean_data['name'])[0]
            try:
                # check condition of the discount fields
                if (int(request.POST['min1']) != "" and
                    int(request.POST['max1']) != "" and
                    int(request.POST['min1']) <= int(request.POST['max1'])):
                    try:
                        tier1_dis = Discount(percentage=float(request.POST['discount1']),
                                            minQuan=int(request.POST['min1']),
                                            maxQuan=int(request.POST['max1']),
                                            product=dis_product)
                        tier1_dis.save()
                    except:
                        messages.error(request,('Discount section 1 is not valid'))
                        return HttpResponseRedirect('registerProduct')
                if (int(request.POST['min2']) != "" and
                    int(request.POST['max2']) != "" and
                    int(request.POST['max1']) < int(request.POST['min2']) and
                    int(request.POST['min2']) <= int(request.POST['max2'])):           
                    try:                           
                        tier2_dis = Discount(percentage = float(request.POST['discount2']),
                                            minQuan= int(request.POST['min2']),
                                            maxQuan= int(request.POST['max2']),
                                            product= dis_product)
                        tier2_dis.save()
                    except:
                        messages.error(request,('Discount section 2 is not valid'))
                        return HttpResponseRedirect('registerProduct')
                if (int(request.POST['min3']) != "" and
                    int(request.POST['max3']) != "" and
                    int(request.POST['max2']) < int(request.POST['min3']) and
                    int(request.POST['min3']) <= int(request.POST['max3'])):  
                    try:              
                        tier3_dis = Discount(percentage = float(request.POST['discount3']),
                                            minQuan= int(request.POST['min3']),
                                            maxQuan= int(request.POST['max3']),
                                            product= dis_product)
                        tier3_dis.save()
                    except:
                        messages.error(request,('Discount section 3 is not valid'))
                        return HttpResponseRedirect('registerProduct')
            except:
                messages.error(request,('Discount section is not valid'))
                HttpResponseRedirect('registerProduct')
            messages.success(request,('You have successfully registered'))
            categories = Category.objects.all()
            return render(request,'category.html', {'categories':categories})
        else:
            messages.error(request,('Form not valid'))
            return HttpResponseRedirect('registerProduct')
    elif request.method == "DELETE":
        if request.user.is_authenticated:
            User.objects.filter(id = request.user.id).delete()
            Customers.objects.filter(user = request.user).delete()
    elif request.method == "GET":
        if (not request.user.is_authenticated or 
                Customers.objects.get(user_id = request.user.id).custLevel != 3):
            messages.error(request,('You are not authorized'))
            return redirect(signin)
        return render(request, "registerProduct.html", {'form': ProductRegistrationForm})
    else:
        return HttpResponse('Unavailable Request', status = status.HTTP_400_BAD_REQUEST)

""" Sets up cart with payment, shipping address, product/shipping cost, and discounts. Processes purchases by inserting information into order
    table and updating 'Your Order' page. Allow user to remove products from cart. """
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
        discount = 0
        for prod in products:
            productPrice = Products.objects.values_list('price', flat = True).get(name = prod.prodName.name)
            obj = {'name': prod.prodName.name, 'price': productPrice, 'quantity': prod.prodQuantity}
            cartList.append(obj)

            if customer.custLevel == 2:
                productObject = Products.objects.get(name=prod.prodName.name)
                discountObject = Discount.objects.filter(product=productObject)
                for deal in discountObject:
                    if prod.prodQuantity >= deal.minQuan and prod.prodQuantity <= deal.maxQuan:
                        discount += (productPrice * prod.prodQuantity) * (deal.percentage/100)
            total += productPrice * prod.prodQuantity
            discount = round(discount, 2)
        if request.method == 'GET':
            return render(request, "cart.html", {'ship': address, 'number': number, 'name': name, 'product': cartList, 'total': total, 'customer': customer.custLevel, 'discount': discount}, status=status.HTTP_200_OK)
        elif request.method == 'POST':
            shippingPrice = request.POST['optradio']
            shippingMethod = ShippingMethod.objects.get(ShipMethPrice = shippingPrice)
            totalPrice = float(total) + float(shippingPrice)
            payment = Payment.objects.get(id=list(paymentid)[0])
            try:
                order = Order.objects.create(customer = customer, orderDate = datetime.date.today(), shippedDate = datetime.date.today(),
                                            totalPrice = totalPrice, payment = payment, shippingAddress = ShippingAddress.objects.get(custID=customer), shippingMethod = shippingMethod)
                order.save()
            except DatabaseError: 
                return HttpResponse(DatabaseErrorMessage, status = status.HTTP_400_BAD_REQUEST)
            Cart.objects.filter(customer=customer).delete()
            messages.success(request,('Your order has been processed!'))
            cartList = []
            return render(request, 'cart.html', {'ship': address, 'number': number, 'name': name, 'product': cartList, 'customer': customer.custLevel, 'discount': discount}, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            product_name = json.loads(request.body.decode('utf-8'))['product']
            u = User.objects.get(id = request.user.id)
            customer = u.customers
            product = Products.objects.all().filter(name = product_name)[0]
            Cart.objects.filter(customer=customer, prodName=product).delete()
            return None
    else:
        return HttpResponse(status = status.HTTP_403_FORBIDDEN)

@csrf_exempt
def about(request):
    return render(request, "about.html", {}, status=status.HTTP_200_OK)

@csrf_exempt
def support(request):
    return render(request, "support.html", {}, status=status.HTTP_200_OK)

     

""" Post a new business application for retailers to apply to buy from the site """
@csrf_exempt
def application(request):
    if request.method == 'GET':
        return render(request, 'application.html', {'form': BusinessApplicationForm}, status=status.HTTP_200_OK)
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
    else:
        return HttpResponse('Unavailable Request', status = status.HTTP_400_BAD_REQUEST)

""" If user is signed in, gets their aacount information """
@csrf_exempt
def account(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            u = User.objects.get(id = request.user.id)
            user = User.objects.get(username=u)
            customer = user.customers
            return render(request, 'account/account.html', {'customer': customer}, status=status.HTTP_200_OK)
    else:
        return HttpResponse(status = status.HTTP_403_FORBIDDEN)

""" Creates or edits address for shipping """
@csrf_exempt
def shipping(request):
    if request.user.is_authenticated:
        u = User.objects.get(id = request.user.id)
        customer = u.customers
        if request.method == 'GET':
            address = ShippingAddress.objects.filter(custID=customer)
            return render(request, 'account/shipping.html', {"ship": address, "customer": customer}, status=status.HTTP_200_OK)
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
            except DatabaseError:
                return HttpReponse(DatabaseErrorMessage, status=HTTP_400_BAD_REQUEST)
            messages.success(request,('Address saved'))
            address = ShippingAddress.objects.filter(custID_id=customer)
            return render(request, "account/shipping.html", {"ship": address, "customer": customer}, status=status.HTTP_200_OK)
    else:
        return HttpResponse(status = status.HTTP_403_FORBIDDEN)

""" Creates or edits payment method """
@csrf_exempt
@sensitive_post_parameters('cardNumber')
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
            return render(request, "account/payment.html", {'number': number, 'name': name}, status=status.HTTP_200_OK)
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
                return HttpResponse(DatabaseErrorMessage, status=status.HTTP_400_BAD_REQUEST)
            """ Update customer table with new payment """
            u = User.objects.get(id = request.user.id)
            user = User.objects.get(username=u)
            customer = user.customers
            customer.PaymentID = payment
            customer.save()
            messages.success(request,('Card saved'))
            return render(request, "account/payment.html", {'number': number, 'name': name}, status=status.HTTP_200_OK)
        else:
            return HttpResponse('Unavailable Request', status = status.HTTP_400_BAD_REQUEST)
    else:
        return HttpResponse(status = status.HTTP_403_FORBIDDEN)

""" Shows history of orders for a signed in user """
@csrf_exempt
def order(request):
    if request.user.is_authenticated:
        u = User.objects.get(id = request.user.id)
        customer = u.customers
        order = Order.objects.filter(customer=customer)
        return render(request, "account/order.html", {'order': order}, status=status.HTTP_200_OK)
    else:
        return HttpResponse(status = status.HTTP_403_FORBIDDEN)


@csrf_exempt
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
        return render(request, "signin.html", {}, status=status.HTTP_200_OK)

@csrf_exempt
def signout(request):
    logout(request)
    messages.success(request,('You have been logged out'))
    return redirect('home')			



""" Registers a new individual user """
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
                try:
                    customer = Customers.objects.create(user = user, custFName = form.cleaned_data['first_name'], custLName = form.cleaned_data['last_name'],
                    custAddress = form.cleaned_data['custAddress'], custCity = form.cleaned_data['custCity'], custZip = form.cleaned_data['custZip'],
                    custState = form.cleaned_data['custState'], custPhone = form.cleaned_data['custPhone'], custLevel = form.cleaned_data['custLevel'])
                    customer.save()
                except DatabaseError:
                    return HttpResponse(DatabaseErrorMessage, status=status.HTTP_400_BAD_REQUEST)
                messages.success(request,('You have successfully registered'))
                return redirect('signin')
        else:
            messages.error(request,('Form not valid'))
            redirect('register')
    elif request.method == "GET":
        return render(request, "register.html", {'form': RegistrationForm}, status=status.HTTP_200_OK)

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
        for discount in range(len(all_discounts)):
            product = Products.objects.all().values().filter(id = all_discounts[discount]['product_id'])[0]
            all_discounts[discount]['product_id'] = product
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
            try:
                product = Products.obejcts.all().filter(id=data['id'])[0]
                product_value = product.values()
            except:
                HttpResponse("Product not found", 
                            safe=False, status = status.HTTP_404_NOT_FOUND)
            if(data['minQuan'] > data['maxQuan']):
                return HttpResponse("minQuan cannot be larger than maxQuan", 
                            safe=False, status = status.HTTP_404_NOT_FOUND)
            new_discount = Discount(percentage = data['percentage'],
                                    minQuan = data['minQuan'],
                                    maxQuan = data['maxQuan'],
                                    product = product)
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
                Customers.objects.get(user_id = request.user.id).custLevel != 3):
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
    elif (request.method == "DELETE"):
        try:
            if (not request.user.is_authenticated or 
                Customers.objects.get(user_id = request.user.id).custLevel != 3):
                return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        except:
            return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        try:
            data = json.loads(request.body.decode('utf-8'))
            discount = Discount.objects.get(id = data['id'])
            # if the key exists it updates the data
            try:
                discount.delete()
                return HttpResponse('Deleted a discount', status=status.HTTP_200_OK)
            except:
                return HttpResponse('Deleteing failed', status=status.HTTP_400_BAD_REQUEST)
        except:
            return HttpResponse('JSON encoding failed', status=status.HTTP_400_BAD_REQUEST)
    else:
        return HttpResponse('Unavailable Request', status = status.HTTP_400_BAD_REQUEST)


@csrf_exempt
def Product_view(request):
    """ THis view is an API for products, see documentation for more detail"""
    if (request.method == "GET"):
        all_products = list(Products.objects.all().values())
        # change the category id to category
        for product in all_products:
            product['category'] = list(Category.objects.all().values().filter(id = product['category_id']))
        return JsonResponse(all_products, safe=False, status=status.HTTP_200_OK)
    elif (request.method == "POST"):
        try:
            if (not request.user.is_authenticated or 
                Customers.objects.get(user_id = request.user.id).custLevel != 3):
                return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        except:
            return HttpResponse('you are not authorized', status=status.HTTP_403_FORBIDDEN)
        try:
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
            new_product = Products(name = data['name'],
                                    description = data['description'],
                                    image = data['image'],
                                    price = data['price'],
                                    category = category,
                                    max_quantity = data['max_quantity'],
                                    min_quantity_retail = data['min_quantity_retail'])
            try:
                new_product.save()
            except:
                return HttpResponse('could not save to the database', 
                        status=status.HTTP_400_BAD_REQUEST)
        except:
            return HttpResponse('json encoding failed', 
                            status=status.HTTP_400_BAD_REQUEST)
        post_product = {
            'name':data['name'],
            'description':data['description'],
            'image':data['image'],
            'price':data['price'],
            'category': Category.objects.all().values().filter(name = data['category'])[0],
            'max_quantity':data['max_quantity'],
            'min_quantity_retail':data['min_quantity_retail']
        }
        return JsonResponse(post_product, safe=False, status=status.HTTP_200_OK)
    elif (request.method == "DELETE"):
        try:
            if (not request.user.is_authenticated or 
                Customers.objects.get(user_id = request.user.id).custLevel != 3):
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
                Customers.objects.get(user_id = request.user.id).custLevel != 3):
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
            product_detail_info.save()
            updated_product = Products.objects.all().values().filter(id=product_id)[0]
            updated_product['category'] = Category.objects.all().values().filter(id = updated_product['category_id'])[0]
            return JsonResponse(updated_product, safe=False, status = status.HTTP_201_CREATED, 
                                        content_type = 'application/json')
        except:
            return HttpResponse('Json Decode Error', status=status.HTTP_400_BAD_REQUEST)
    else:
        return HttpResponse('Unavailable Request', status = status.HTTP_400_BAD_REQUEST)
