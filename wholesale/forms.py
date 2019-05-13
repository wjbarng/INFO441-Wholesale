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

class ShippingAddressForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=30, required=True)
    first_name = forms.CharField(label='First Name', max_length=30, required=True)
    last_name = forms.CharField(label='Last Name', max_length=30, required=True)
    address = forms.CharField(label='Address', max_length=30, required=True)
    city = forms.CharField(label='City', max_length=30, required=True)
    state = forms.CharField(label='State (2 letter abbreviation)', max_length=2, required=True)
    shipZip = forms.CharField(label='Zip', max_length=30, required=True)
    phone = forms.CharField(label='Phone Number', max_length=30, required=True)