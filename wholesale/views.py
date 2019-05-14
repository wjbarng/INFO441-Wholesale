from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .forms import RegistrationForm, ShippingAddressForm, BusinessApplicationForm
from django.contrib.auth.models import User
from wholesale.models import Customers, Payment, ShippingAddress, BusinessApplication
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view

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

""" Post a new business application or delete an application by business name """
@csrf_exempt
@api_view(['GET', 'POST', 'DELETE'])
def application(request):
    if request.method == 'GET':
        return render(request, 'application.html', {'form': BusinessApplicationForm})
    elif request.method == 'POST':
        form = BusinessApplicationForm(request.POST)
        if form.is_valid():
            application = BusinessApplication.objects.create(busName = form.cleaned_data['busName'], busAddress = form.cleaned_data['busAddress'], 
                                                             busZip = form.cleaned_data['busZip'], busCity = form.cleaned_data['busCity'], 
                                                             busState = form.cleaned_data['busState'], busEmail = form.cleaned_data['busEmail'], 
                                                             busPhone = form.cleaned_data['busPhone'])
            application.save()
            messages.success(request,('Application submitted'))
            return redirect('home')
        else:
            messages.error(request,('Application form not valid'))
            return redirect('application')
    elif request.method == 'DELETE':
        data = request.data
        BusinessApplication.objects.filter(busName = data['name']).delete()
        return HttpResponse("Delete successful")


""" Creates new address for shipping or deletes address associated with user """
@csrf_exempt
@api_view(['GET', 'POST', 'DELETE'])
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
                return render(request, "account.html", {'fname': form.cleaned_data['first_name'], 'lname': form.cleaned_data['last_name'],
                                'city': form.cleaned_data['city'], 'state': form.cleaned_data['state'], 'zip': form.cleaned_data['shipZip'],
                                'address': form.cleaned_data['address'], 'phone': form.cleaned_data['phone']})
            else:
                messages.error(request,('Address form not valid'))
                return redirect('account')
    elif request.method == "DELETE":
        if request.user.is_authenticated:
            u = User.objects.get(id = request.user.id)
            customer = u.customers
            shippingAddress = ShippingAddress.objects.filter(custID = customer).delete()
            return HttpResponse("Delete successful")



    

""" Update and create new account information """
@csrf_exempt
@api_view(['GET', 'POST', 'PATCH'])
def account(request):
    if request.method == 'PATCH':
        if request.user.is_authenticated:
            """ Update password for user """
            data = request.data
            u = User.objects.get(id = request.user.id)
            u.password = data['password']
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
@csrf_exempt
@api_view(['GET', 'POST'])
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



""" Registers a new individual user on post, deletes user on delete,
    and gets the register form on get """
@csrf_exempt
@api_view(['GET', 'POST', 'DELETE'])
def register(request):
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
            return HttpResponse("Delete successful")
    elif request.method == "GET":
        return render(request, "register.html", {'form': RegistrationForm})

