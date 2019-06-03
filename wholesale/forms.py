from django import forms


class RegistrationForm(forms.Form):
    username = forms.CharField(label='Username', max_length=30, required=True)
    password = forms.CharField(label='Password', max_length=30, required=True, widget=forms.PasswordInput())
    passwordconf = forms.CharField(label='Password Confirmation', max_length=30, required=True, widget=forms.PasswordInput())
    email = forms.EmailField(label='Email', max_length=30, required=True)
    first_name = forms.CharField(label='First Name', max_length=30, required=True)
    last_name = forms.CharField(label='Last Name', max_length=30, required=True)
    custAddress = forms.CharField(label='Address', max_length=30, required=True)
    custCity = forms.CharField(label='City', max_length=30, required=True)
    custState = forms.CharField(label='State (2 letter abbreviation)', max_length=2, required=True)
    custZip = forms.CharField(label='Zip', max_length=30, required=True)
    custPhone = forms.CharField(label='Phone Number', max_length=30, required=True)
    LEVEL_CHOICES = (
        (1, 'individual'),
        (2, 'business'),
        (3, 'admin')
    )
    custLevel = forms.ChoiceField(required=True, choices=LEVEL_CHOICES)

class ShippingAddressForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=30, required=True)
    first_name = forms.CharField(label='First Name', max_length=30, required=True)
    last_name = forms.CharField(label='Last Name', max_length=30, required=True)
    address = forms.CharField(label='Address', max_length=30, required=True)
    city = forms.CharField(label='City', max_length=30, required=True)
    state = forms.CharField(label='State (2 letter abbreviation)', max_length=2, required=True)
    shipZip = forms.CharField(label='Zip', max_length=30, required=True)
    phone = forms.CharField(label='Phone Number', max_length=30, required=True)

class ProductRegistrationForm(forms.Form):
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
    name = forms.CharField(label='Name', max_length=50, required=True)
    description = forms.CharField(label='Description', max_length=100)
    image = forms.URLField(required=False, max_length=200)
    price = forms.FloatField(required=True)
    category = forms.ChoiceField(required=True, choices=CATEGORY_CHOICES)
    max_quantity = forms.IntegerField(required=True)
    min_quantity_retail = forms.IntegerField(required=True)
    
class BusinessApplicationForm(forms.Form):
    busName = forms.CharField(label='Business Name', max_length=30, required=True)
    busAddress = forms.CharField(label='Business Address', max_length=30, required=True)
    busZip = forms.CharField(label='Zip', max_length=30, required=True)
    busCity = forms.CharField(label='City', max_length=30, required=True)
    busState = forms.CharField(label='State (2 letter abbreviation)', max_length=2, required=True)
    busEmail = forms.EmailField(label='Business Email Address', max_length=30, required=True)
    busPhone = forms.CharField(label='Business Phone Number', max_length=30, required=True)
