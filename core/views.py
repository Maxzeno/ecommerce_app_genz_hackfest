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

# Create your views here.


class VerifyPaystackPayment(LoginRequiredMixin, Base):
	PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
	paystack_base_url = 'https://api.paystack.co'

	def get_request(self, request, ref): 
		verify_payment = self.verify_payment(ref)

		if verify_payment['status']:
			messages.success(request, "Your payment is processing")
			return redirect(reverse('core:orders'))
			
		messages.warning(request, "Your payment failed you may need to contact admin")
		return redirect(reverse('main:contact'))


	def verify_payment(self, ref, *args, **kwargs):
		path = f"/transaction/verify/{ref}"
		headers = {
			"Authorization": f"Bearer {self.PAYSTACK_SECRET_KEY}",
			"Content-Type": "application/json"
		}
		url = self.paystack_base_url + path

		res = requests.get(url, headers=headers)
		res_data = res.json()
		return res_data


class TransferPayment(LoginRequiredMixin, Base):
	def post_request(self, request):
		try:
			with transaction.atomic():
				payment_prove_form = PaymentProveForm(request.POST, request.FILES)

				order = Order()
				items = CartModel.objects.filter(buyer=request.user, checked_out=False)
				order.buyer = request.user
				order.save()
				order.items.set(items)

				# get the image from the form
				image_field = request.FILES['image']

				payment_prove = TransferPaymentModel(buyer=request.user, order=order, image=image_field)
				payment_prove.save()
				items.update(checked_out=True)

				messages.success(request, 'Transfer prove submitted admin will review')
				return redirect(reverse('core:orders'))
		except Exception:
			messages.warning(request, 'An error occured try again')
			return redirect(reverse('core:checkout'))


class Checkout(LoginRequiredMixin, Base):
	def get_request(self, request):
		if not request.user.state and not request.user.address:
			request.session['back_to_checkout'] = 'core:checkout'
			messages.warning(request, 'Add state and address before you can checkout')
			return redirect(reverse('core:address'))


		payment_prove_form = PaymentProveForm()
		items = CartModel.objects.filter(buyer=request.user, checked_out=False)
		PAYSTACK_PUBLIC_KEY = settings.PAYSTACK_PUBLIC_KEY
		
		bank_account = TransferBankAccount.objects.order_by('-date').first()
		delivery_price = DeliveryPrice.objects.order_by('-date').first()

		total = 0
		for item in items:
			total += item.total_price()

		if delivery_price:
			total += delivery_price.price

		paystack_total = total * 100 # this is because paystack 100 == 1 naira
		
		items_str = ''
		for i in items.values_list('pk'):
			items_str += f'{i[0]} '

		return (request, 'core/checkout.html', {
			'total': '{:,.2f}'.format(total), 
			'paystack_total': paystack_total,
			'items': items, 
			'items_str': items_str.strip(),
			'nav_account': 'green',
			'PAYSTACK_PUBLIC_KEY': PAYSTACK_PUBLIC_KEY,
			'payment_prove_form': payment_prove_form,
			'bank_account': bank_account,
			'delivery_price': delivery_price,
		})


class Cart(LoginRequiredMixin, Base):
	def get_request(self, request):
		items = CartModel.objects.filter(buyer=request.user, checked_out=False)
		total = 0
		for item in items:
			total += item.total_price()
		return (request, 'core/cart.html', {'cart_items': items, 'total': '{:,.2f}'.format(total), 'nav_account': 'green'})


class CartAddRemove(LoginRequiredMixin, View):
	def post(self, request):
		data = json.loads(request.body.decode('utf-8'))
		product_pk = data.get('product')
		items = data.get('items')
		remove = data.get('remove')
		is_reduce = data.get('is_reduce')

		product = Product.objects.filter(pk=product_pk).first()

		if not product or not product.is_approved:
			return JsonResponse({'ok': False})

		total = 0
		for item in items:
			cart_item, created = CartModel.objects.get_or_create(buyer=request.user, product=product, product_size=item, checked_out=False)

		to_delete = CartModel.objects.filter(buyer=request.user, product=product, checked_out=False)\
			.exclude(product_size__in=items)
		to_delete.delete()

		if not items and not is_reduce:
			cart_item, created = CartModel.objects.get_or_create(buyer=request.user, product=product, checked_out=False)

		if remove:
			to_delete = CartModel.objects.filter(buyer=request.user, product=product, checked_out=False)
			to_delete.delete()

		num_in_cart = CartModel.objects.filter(buyer=request.user, checked_out=False).count()

		return JsonResponse({'ok': True, 'num_in_cart': num_in_cart})


class CartPlus(LoginRequiredMixin, Base):
	def get_request(self, request, pk):
		cart_item = CartModel.objects.filter(pk=pk).first()
		if not cart_item:
			return JsonResponse({'ok': False})

		cart_item.quantity += 1
		cart_item.save()

		total = 0
		items = CartModel.objects.filter(buyer=request.user, checked_out=False)
		for item in items:
			total += item.total_price()

		return JsonResponse({'ok': True, 
			'price': '{:,.2f}'.format(cart_item.product.price * cart_item.quantity), 
			'total': '{:,.2f}'.format(total)
			})


class CartMinus(LoginRequiredMixin, Base):
	def get_request(self, request, pk):
		cart_item = CartModel.objects.filter(pk=pk).first()
		if not cart_item:
			return JsonResponse({'ok': False})

		cart_item.quantity = cart_item.quantity -1 if cart_item.quantity > 1 else 1
		cart_item.save()

		total = 0
		items = CartModel.objects.filter(buyer=request.user, checked_out=False)
		for item in items:
			total += item.total_price()

		return JsonResponse({'ok': True, 
			'price': '{:,.2f}'.format(cart_item.product.price * cart_item.quantity), 
			'total': '{:,.2f}'.format(total)
			})


class CartRemove(LoginRequiredMixin, Base):
	def get_request(self, request, pk):
		cart_item = CartModel.objects.filter(pk=pk).first()
		if not cart_item:
			return JsonResponse({'ok': False})

		cart_item.delete()

		items = CartModel.objects.filter(buyer=request.user, checked_out=False)
		total = 0
		for item in items:
			total += item.total_price()
		return JsonResponse({'ok': True, 'total': '{:,.2f}'.format(total)})


# lots of bugs
class OrderCreate(LoginRequiredMixin, Base):
	def get_request(self, request, pk):
		return redirect(reverse('core:order_detail', kwargs={'pk': pk}))

	def post_request(self, request, pk):
		# body
		# return redirect(reverse('core:order_detail', kwargs={'pk':order.pk}))
		pass


class OrderDetail(LoginRequiredMixin, Base):
	def get_request(self, request, pk):
		""" This order details creates an order if given product id"""
		order = Order.objects.filter(pk=pk).first()
		if order:
			return (request, 'core/order_detail.html', {'order': order, 'nav_account': 'green'})
		messages.warning(request, 'Click order if you want to continue your request')
		return redirect(reverse('main:product_detail', kwargs={'pk': pk}))


class Orders(LoginRequiredMixin, Base):
	def get_request(self, request):
		orders = Order.objects.filter(buyer=request.user.id).order_by('-date')
		return (request, 'core/orders.html', {'orders': orders, 'nav_account': 'green'})


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


class Settings(LoginRequiredMixin, Base):
	def get_request(self, request):
		user = request.user
		data_form = UserDataForm({'name': user.name, 'number': user.number, 'image': user.image, 'image': user.image})
		password_form = UserPasswordForm(user=user)
		return (request, 'core/settings.html', {'data_form': data_form, 'password_form': password_form, 'nav_account': 'green'})


class UserData(LoginRequiredMixin, View):
	def get(self, request):
		return redirect(reverse('core:settings'))

	def post(self, request):
		form = UserDataForm(request.POST, request.FILES)
		if form.is_valid():
			user = User.objects.get(pk=request.user.id)
			user.name = form.cleaned_data.get('name')
			user.number = form.cleaned_data.get('number')
			if form.cleaned_data.get('image'):
				user.image = form.cleaned_data.get('image')
			user.save()
			messages.success(request, 'User data updated')
			return redirect(reverse('core:settings'))

		messages.warning(request, 'Fill the user form appropriately')
		return redirect(reverse('core:settings'))


class UserPassword(LoginRequiredMixin, View):
	def get(self, request):
		return redirect(reverse('core:settings'))

	def post(self, request):
		form = UserPasswordForm(request.POST, user=request.user)
		if form.is_valid():
			user = User.objects.get(pk=request.user.id)
			password = form.cleaned_data.get('password')
			user.password = password
			user.save()
			messages.success(request, 'User password updated')
			return redirect(reverse('core:settings'))

		messages.warning(request, 'Fill the password form appropriately')
		return redirect(reverse('core:settings'))

