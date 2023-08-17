from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from .models import (
	User, Order, Product, Cart as CartModel, TransferPayment as TransferPaymentModel, TransferBankAccount, DeliveryPrice)
from .forms import UserDataForm, UserPasswordForm, AddressForm, PaymentProveForm
from main.views import Base


class Address(LoginRequiredMixin, Base):
	def get_request(self, request):
		user = request.user
		address_form = AddressForm({'state': user.state, 'address': user.address})
		return (request, 'core/address.html', {'address_form': address_form, 'nav_account': 'green'})

	def post_request(self, request):
		form = AddressForm(request.POST)
		if form.is_valid():
			user = User.objects.get(pk=request.user.id)
			user.state = form.cleaned_data.get('state')
			user.address = form.cleaned_data.get('address')
			user.save()
			messages.success(request, 'User address updated')
			back_to_checkout = request.session.pop('back_to_checkout', None)
			if back_to_checkout:
				return redirect(reverse(back_to_checkout))

			return (request, 'core/address.html', {'address_form': form, 'nav_account': 'green'})

		messages.warning(request, 'Fill the user address form appropriately')
		return redirect(reverse('core:address'))

