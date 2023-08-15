from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.db.utils import IntegrityError
from django.contrib import messages
from django.http import Http404, HttpResponse, JsonResponse, HttpResponseRedirect, QueryDict
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from core.models import (
	Category, Order, SubCategory, Product, User, Email, 
	ContactUs as ContactUsModel, Cart, Cart as CartModel, DeliveryPrice
	)
from utils import popular_categories, popular_categories_and_sub, paginate_page, is_mobile
from .forms import EmailForm, ContactUsForm

# Create your views here.


def error_404(request, exception):
	return render(request, 'main/404.html', context={'msg': "requested page not found"}, status=404)

# def error_500(request):
    # return render(request, 'main/500.html', status=500)


class Base(View):
	base_context = {**popular_categories(), 'cart_items': [], 'product_in_cart': []}
	def get(self, request, *args, **kwargs):
		if request.user.is_authenticated:
			items = Cart.objects.filter(buyer=request.user, checked_out=False, product__is_approved=True)
			self.base_context['cart_items'] = items
			product_in_cart = set()
			for item in items:
				if item.product.is_approved:
					product_in_cart.add(item.product.pk)
			self.base_context['product_in_cart'] = product_in_cart

		data = self.get_request(request, *args, **kwargs)
		if isinstance(data, (HttpResponseRedirect, HttpResponse)):
			return data

		request_obj, template, context = data
		context.update(self.base_context)
		return render(request_obj, template, context)

	def post(self, request, *args, **kwargs):
		data = self.post_request(request, *args, **kwargs)
		if isinstance(data, (HttpResponseRedirect, HttpResponse)):
			return data
		return render(*data)
		

class Index(Base):
	def get_request(self, request):
		is_mobile_device = is_mobile(request)
		if is_mobile_device:
			no_products  = 8
		else:
			no_products = 12

		products = Product.objects.filter(is_approved=True).order_by('ordered')[:no_products]
		return (request, 'main/index.html', {'products': products, 'email_form': EmailForm(), 'nav_home': 'green'})


class ProductDetail(Base):
	def get_request(self, request, pk):
		product = get_object_or_404(Product, pk=pk)
		btn_disable = False
		if not product.is_approved:
			if not request.user.is_authenticated or not request.user.is_superuser:
				raise Http404("The product you requested does not exist or is disapproved")

			if request.user.is_authenticated and request.user.is_superuser:
				messages.warning(request, 'The product request is not approved')
				btn_disable = True


		is_mobile_device = is_mobile(request)
		if is_mobile_device:
			no_products  = 4
		else:
			no_products = 6

		items = []
		sizes_in_cart = []
		if request.user.is_authenticated:
			items = Cart.objects.filter(buyer=request.user, product=product, checked_out=False, product__is_approved=True)
			sizes_in_cart = [ '' if not i.product_size else i.product_size for i in items ]

		single_item_no_size = None
		if len(items) == 1 and not items[0].product_size:
			single_item_no_size = items[0]

		related_products = Product.objects\
		.filter(Q(sub_category=product.sub_category) & Q(is_approved=True))\
		.exclude(pk=product.pk).order_by('ordered')[:no_products]

		return (request, 'main/product_detail.html', {
			'product': product, 
			'products': related_products,
			'sizes_in_cart': sizes_in_cart,
			'single_item_no_size': single_item_no_size,
			'nav_products': 'green',
			'btn_disable': btn_disable,
		})


class Products(Base):
	def get_request(self, request):
		category_name = request.GET.get('category')
		sub_name = request.GET.get('sub')
		search = request.GET.get('search')

		category = None
		sub_category = None
		agrs = ''

		has_no_filter_search = False

		if not search:

			if category_name:
				category = Category.objects.filter(name=category_name).first()

				if sub_name:
					sub_category = SubCategory.objects.filter(Q(name=sub_name) & Q(category=category)).first()

			if sub_category:
				agrs += f'&category={category_name}&sub={sub_name}'
				the_products = Product.objects.filter(Q(sub_category=sub_category) & Q(is_approved=True)).order_by('ordered')
			elif category:
				agrs += f'&category={category_name}'
				the_products = Product.objects.filter(Q(sub_category__category=category) & Q(is_approved=True)).order_by('ordered')
			else:
				has_no_filter_search = True
				the_products = Product.objects.filter(is_approved=True).order_by('ordered')
		else:
			the_products = Product.objects.filter(Q(is_approved=True) & Q(name__icontains=search)).order_by('ordered')[:12]

		context = {
			**paginate_page(the_products, request, Http404, obj='products'),
			**popular_categories_and_sub(),
			'number_of_products': len(the_products),
			'url_args': agrs,
			'nav_products': 'green',
			'search_term': search,
			'has_no_filter_search': has_no_filter_search,
		}

		return (request, 'main/products.html', context)


class ContactUs(Base):
	def get_request(self, request):
		form = ContactUsForm()
		return (request, 'main/contact_us.html', {'form': form, 'nav_contact_us': 'green'})

	def post_request(self, request):
		form = ContactUsForm(request.POST)
		if form.is_valid():
			try:
				ContactUsModel.objects.create(email=form.cleaned_data.get('email'), message=form.cleaned_data.get('message'))
				messages.success(request, 'Message has been received')
				form = ContactUsForm()
				return (request, 'main/contact_us.html', {'form': form})

			except IntegrityError:
				messages.warning(request, 'Fill email and message appropriately')
				return (request, 'main/contact_us.html', {'form': form})

		messages.warning(request, 'Fill email and message appropriately')
		return (request, 'main/contact_us.html', {'form': form})


class EmailSubscribe(View):
	def get(self, request):
		return redirect(reverse('main:index'))

	def post(self, request):
		email_form = EmailForm(request.POST)
		if email_form.is_valid():
			try:
				Email.objects.create(email=email_form.cleaned_data.get('email'))
				messages.success(request, 'Email address has been added')
				return redirect(reverse('main:index'))

			except IntegrityError:
				messages.warning(request, 'Email address is invalid or already exists')
				return redirect(reverse('main:index'))

		messages.warning(request, 'Email address is invalid or already exists')
		return redirect(reverse('main:index'))
