from django import forms
from django.contrib import messages
from .models import User


class PaymentProveForm(forms.Form):
	image = forms.ImageField(required=False, label='', widget=forms.FileInput(attrs={
		'class': 'form-control'
	}))


class ProductDeleteForm(forms.Form):
	pk = forms.CharField(required=True, label='', max_length=100,  widget=forms.TextInput(attrs={
		'type': 'hidden'
		}))


class AddressForm(forms.Form):
	state = forms.CharField(required=True, label='', max_length=100,  widget=forms.TextInput(attrs={
		'placeholder':'State', 'class': 'form-control'
		}))

	address = forms.CharField(required=True, label='', max_length=1000,  widget=forms.TextInput(attrs={
		'placeholder':'Address', 'class': 'form-control'
		}))

	def clean_state(self):
		state = self.cleaned_data.get('state')
		if not state or len(state) == 0:
			raise forms.ValidationError('State is required')
		return state
		
	def clean_address(self):
		address = self.cleaned_data.get('address')
		if not address or len(address) == 0:
			raise forms.ValidationError('Address is required')
		return address


class UserDataForm(forms.Form):
	name = forms.CharField(required=True, label='', max_length=100,  widget=forms.TextInput(attrs={
		'placeholder':'Name', 'class': 'form-control'
		}))

	number = forms.CharField(required=True, label='', max_length=30,  widget=forms.TextInput(attrs={
		'placeholder':'Number', 'class': 'form-control'
		}))
	
	image = forms.ImageField(required=False, label='', widget=forms.FileInput(attrs={
		'class': 'form-control'
	}))

	def clean_name(self):
		name = self.cleaned_data.get('name')
		if not name or len(name) == 0:
			raise forms.ValidationError('Name is required')
		return name
		
	def clean_number(self):
		whatsapp_number = self.cleaned_data.get('whatsapp_number')
		if not whatsapp_number or len(whatsapp_number) == 0:
			raise forms.ValidationError('Whatsapp number is required')
		return whatsapp_number


class UserPasswordForm(forms.Form):
	password = forms.CharField(required=True, label='', max_length=128, widget=forms.PasswordInput(attrs={
		'placeholder':'**********', 'class': 'form-control',
		}))

	current_password = forms.CharField(required=True, label='', max_length=128, widget=forms.PasswordInput(attrs={
		'placeholder':'**********', 'class': 'form-control',
		}))

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user', '')
		super(UserPasswordForm, self).__init__(*args, **kwargs)

	def clean_password(self):
		password = self.cleaned_data.get('password')

		if not password or len(password) < 8:
			raise forms.ValidationError('Password should be greater than 7 characters')

		return password

	def clean_current_password(self):
		current_password = self.cleaned_data.get('current_password')

		if not self.user.check_password(current_password):
			print('invalid')
			raise forms.ValidationError('Invalid password')
		print('valid')
		return current_password
            




