from django.shortcuts import redirect
from django import forms
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from core.models import User


class SigninForm(forms.Form):
	email = forms.EmailField(required=True, label='', max_length=100,  widget=forms.EmailInput(attrs={
		'placeholder':'Email', 'class': 'form-control', 'id': 'inputEmail4'
		}))
	password = forms.CharField(required=True, label='', max_length=128, widget=forms.PasswordInput(attrs={
		'placeholder':'Enter Password', 'class': 'form-control', 'id': 'fakePassword'
		}))
	remember = forms.CharField(required=False, label='', max_length=128, widget=forms.CheckboxInput(attrs={
		'class': 'form-check-input', 'id': 'flexCheckDefault'
		}))


class SignupForm(forms.Form):
	name = forms.CharField(required=False, label='', max_length=100,  widget=forms.TextInput(attrs={
		'placeholder':'Name', 'class': 'form-control'
		}))
	email = forms.EmailField(required=True, label='', max_length=100,  widget=forms.EmailInput(attrs={
		'placeholder':'Email', 'class': 'form-control', 'id': 'inputEmail4'
		}))
	number = forms.CharField(required=True, label='', max_length=30,  widget=forms.TextInput(attrs={
		'placeholder':'Number', 'class': 'form-control'
		}))
	password = forms.CharField(required=True, label='', max_length=128, widget=forms.PasswordInput(attrs={
		'placeholder':'Enter Password', 'class': 'form-control', 'id': 'fakePassword'
		}))

	def clean_email(self):
		email = self.cleaned_data.get('email')
		found_email = User.objects.filter(email=email.lower()).first()
		if found_email:
			raise forms.ValidationError('Email Exists')
		return email.lower()

	def clean_password(self):
		password = self.cleaned_data.get('password')
		if len(password) < 8 or len(password) > 128:
			if len(password) < 8:
				raise forms.ValidationError('Password should be greater than 7 characters')
			raise forms.ValidationError('Password should be less than 129 characters')

		elif password.isnumeric() or password.isalpha():
			raise forms.ValidationError('Password should contain alphabets and numbers')

		return password
            

class ForgotPasswordForm(forms.Form):
	email = forms.EmailField(required=True, label='', max_length=100,  widget=forms.EmailInput(attrs={
		'placeholder':'Email', 'class': 'form-control', 'id': 'inputEmail4'
		}))


class ResetPasswordForm(forms.Form):
	password = forms.CharField(required=True, label='', max_length=128, widget=forms.PasswordInput(attrs={
		'placeholder':'Enter Password', 'class': 'form-control', 'id': 'fakePassword'
		}))

	confirm_password = forms.CharField(required=True, label='', max_length=128, widget=forms.PasswordInput(attrs={
		'placeholder':'Confirm Password', 'class': 'form-control', 'id': 'fakePassword2'
		}))

	def clean_password(self):
		password = self.cleaned_data.get('password')

		if len(password) < 8 or len(password) > 128:
			if len(password) < 8:
				raise forms.ValidationError('Password should be greater than 7 characters')
			raise forms.ValidationError('Password should be less than 129 characters')

		elif password.isnumeric() or password.isalpha():
			raise forms.ValidationError('Password should contain alphabets and numbers')

		return password

	def clean_confirm_password(self):
		password = self.cleaned_data.get('password')
		confirm_password = self.cleaned_data.get('confirm_password')

		if password and password != confirm_password:
			raise forms.ValidationError('The two passwords don\'t match')

		return confirm_password
            




