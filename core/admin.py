from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django_summernote.models import Attachment
from ckeditor.widgets import CKEditorWidget

# from django_summernote.widgets import SummernoteWidget

from .models import (
    User, Category, SubCategory, Product, Order, 
    Email, ContactUs, TransferPayment, Cart, DeliveryPrice, TransferBankAccount
    )

# Register your models here.

admin.site.site_title = 'Unique Favor Store Admin'
admin.site.index_title = 'Welcome to Unique Favor Store'
admin.site.site_header = format_html('<a href="/adminuser/admin/"><img src="/static/img/icon nobg-crop.png" style="height: 100px"></a>')

admin.site.unregister(Group)
admin.site.unregister(Attachment)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fields = ('name', 'email', 'number', 'password', 'description', 'state', 'address', 'image', 'is_superuser', 'is_active', 'is_suspended')
    list_display = ('name', 'email', 'number', 'is_superuser', 'is_active', 'is_suspended', 'date_joined')
    order = ('name',)
    search_fields = ('name', 'email')
    list_filter = ('is_superuser', 'is_active', 'is_suspended', 'date_joined')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'date')
    search_fields = ('name',)
    exclude = ('date', 'ordered')
    list_filter = ('date',)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'category', 'date')
    search_fields = ('name',)
    exclude = ('date', 'ordered')
    list_filter = ('category', 'date')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    fields = ('id', 'name', 'description', 'state', 'image', 'image2', 'image3', 'sub_category', 'price', 'data', 'is_approved')
    list_display = ('id', 'name', 'sub_category', 'state', 'price', 'is_approved', 'date')
    search_fields = ('name','id')
    exclude = ('ordered',)
    readonly_fields = ('id',)
    list_filter = ('is_approved', 'sub_category', 'state', 'date')
    formfield_overrides = {
        'RichTextField': {'widget': CKEditorWidget}
    }


# i think i will not register this model so it doesn't show in the admin
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    fields = ('buyer', 'product', 'quantity', 'product_size', 'checked_out', 'price_ordered_at')
    list_display = ('buyer', 'product', 'quantity', 'product_size', 'checked_out', 'price_ordered_at', 'date')
    search_fields = ('buyer', 'product', 'quantity')
    list_filter = ('product', 'buyer', 'quantity', 'checked_out', 'date')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    fields = ('id', 'buyer', 'items', 'paid', 'delivery_fee', 'paystack_ref', 'status', 'has_paid', 'incomplete_payment')
    list_display = ('id', 'buyer', 'paid', 'paystack_ref', 'delivery_fee', 'status', 'has_paid', 'incomplete_payment', 'date')
    search_fields = ('id',)
    readonly_fields = ('id',)
    list_filter = ('status', 'items', 'has_paid', 'buyer', 'date')


@admin.register(TransferPayment)
class TransferPaymentAdmin(admin.ModelAdmin):
    fields = ('image', 'buyer', 'order', 'confirmed', 'checked')
    list_display = ('buyer', 'order', 'confirmed', 'checked', 'date')
    search_fields = ('buyer',)
    list_filter = ('confirmed', 'checked', 'buyer', 'date')


@admin.register(TransferBankAccount)
class TransferBankAccountAdmin(admin.ModelAdmin):
    list_display = ('bank_name', 'bank_number', 'account_name', 'date')
    search_fields = ('bank_name',)
    list_filter = ('date',)


@admin.register(DeliveryPrice)
class DeliveryPriceAdmin(admin.ModelAdmin):
    list_display = ('price', 'date')
    search_fields = ('price',)
    list_filter = ('date',)


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('email', 'date')
    search_fields = ('email',)
    list_filter = ('date',)


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_resolved', 'date')
    search_fields = ('email',)
    list_filter = ('is_resolved', 'date')


