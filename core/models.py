from django.db import models
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from django.utils import timezone
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db.models import Q
from django.contrib.auth.hashers import (
    check_password, is_password_usable, make_password,
)
from django.contrib.postgres.fields import JSONField
from ckeditor.fields import RichTextField
import shortuuid


# Create your models here.

class MyUserManager(BaseUserManager):
	use_in_migrations = True

	def _create_user(self, email, password, **extra_fields):
		"""
		Create and save a user with the given, email, and password.
		"""
		email = self.normalize_email(email)
		user = self.model(email=email, password=password, **extra_fields)
		user.save(using=self._db)
		return user

	def create(self, email=None, password=None, **extra_fields):
		extra_fields.setdefault('is_superuser', False)
		return self._create_user(email, password, **extra_fields)

	def create_user(self, email=None, password=None, **extra_fields):
		extra_fields.setdefault('is_superuser', False)
		return self._create_user(email, password, **extra_fields)

	def create_superuser(self, email=None, password=None, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError('Superuser must have is_staff=True.')
		if extra_fields.get('is_superuser') is not True:
			raise ValueError('Superuser must have is_superuser=True.')

		return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    number = models.CharField(max_length=30)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    _password = ''
    state = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    is_staff = models.BooleanField(default=False, help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(default=True)
    is_suspended = models.BooleanField(default=False)
    ordered = models.IntegerField(default=0)
    date_joined = models.DateTimeField(default=timezone.now)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = MyUserManager()

    def save(self, *args, **kwargs):
        u = self.__class__.objects.filter(pk=self.pk).first()
        if not u or u and u.password != self.password:
            self.set_password(self.password)

        if u and not u.is_superuser and self.is_superuser:
            self.is_staff = True

        super(User, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.name or self.email


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    ordered = models.IntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)

    def inc_order(self):
        self.ordered += 1
        self.save()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    ordered = models.IntegerField(default=0)
    date = models.DateTimeField(default=timezone.now)

    def inc_order(self):
        self.ordered += 1
        self.save()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Sub Categories'

        constraints = [
            models.UniqueConstraint(
                fields=['category', 'name'],
                name='unique_name_per_category'
            )
        ]

        
def unique_id(model):
    while True:
        random = shortuuid.ShortUUID().random(length=8)
        if not model.objects.filter(id=random).exists():
            break
    return random

def product_id():
    return unique_id(Product)

def order_id():
    return unique_id(Order)


class DeliveryPrice(models.Model):
    price = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)


class TransferBankAccount(models.Model):
    bank_name = models.CharField(max_length=100)
    account_name = models.CharField(max_length=250)
    bank_number = models.CharField(max_length=10)
    date = models.DateTimeField(default=timezone.now)


class Product(models.Model):
    id = models.CharField(primary_key=True, max_length=10, default=product_id)
    # data = JSONField() ## will store size and maybe color and quantity for each
    name = models.CharField(max_length=100)
    data = models.JSONField(blank=True, null=True)
    description = RichTextField(blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    image2 = models.ImageField(upload_to='images/', blank=True, null=True)
    image3 = models.ImageField(upload_to='images/', blank=True, null=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    ordered = models.IntegerField(default=0)
    is_approved = models.BooleanField(default=True)
    date = models.DateTimeField(default=timezone.now)

    def inc_order(self):
        self.ordered += 1
        self.save()

    def __str__(self):
        return self.name

    def is_approved_status(self):
        if self.is_approved:
            return 'Approved'
        return 'Not Approved'
    

class Cart(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_size = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    checked_out = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)
    price_ordered_at = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def paid_check_out(self):
        self.checked_out = True
        self.product.inc_order()
        self.product.sub_category.inc_order()
        self.product.sub_category.category.inc_order()

        if not self.price_ordered_at:
            self.price_ordered_at = self.product.price
        self.save()

    def total_price(self):
        if self.price_ordered_at:
            return round(self.price_ordered_at * self.quantity, 2)
        return round(self.product.price * self.quantity, 2)

    def checked_out_status(self):
        if self.checked_out:
            return 'Yes'
        return 'No'

    def __str__(self):
        return f"{self.buyer.name} - {self.product.name} x {self.quantity} - checked out: {self.checked_out_status()}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('S', 'Success'),
        ('P', 'Pending'),
        ('C', 'Cancel'),
    ]

    id = models.CharField(primary_key=True, max_length=10, default=order_id)
    paystack_ref = models.CharField(max_length=100, null=True, blank=True)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(Cart)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    paid = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    delivery_fee = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    has_paid = models.BooleanField(default=False)
    incomplete_payment = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.has_paid:
            # i thing we have an issue here which happens when we try to create order from admin
            print(self.items.all(), 'self.items.all()')
            for item in self.items.all():
                item.paid_check_out()

        super().save(*args, **kwargs)

    def get_total_price_now(self):
        price = 0
        for item in self.items.all():
            price += item.total_price()
        return price

    def order_status(self):
        for i in self.STATUS_CHOICES:
            if i[0].upper() == self.status.upper():
                return i[1]
        return ''

    def has_paid_status(self):
        if self.has_paid:
            return 'Yes'
        return 'No'

    def __str__(self):
        return f"{self.id}"


class TransferPayment(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
    confirmed = models.BooleanField(default=False)
    checked = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)


class Email(models.Model):
    email = models.EmailField(unique=True, null=False)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email
    

class ContactUs(models.Model):
    email = models.EmailField(unique=True)
    message = models.CharField(max_length=1000)
    date = models.DateTimeField(default=timezone.now)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name_plural = 'Contact us'
