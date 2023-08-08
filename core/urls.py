from django.urls import path
from .views import (Settings, UserData, UserPassword, Address, Orders, OrderDetail, OrderCreate,
		Cart, CartAddRemove, CartPlus, CartMinus, CartRemove, Checkout, VerifyPaystackPayment, TransferPayment)

app_name = 'core'

urlpatterns = [
    path('transfer-payment', TransferPayment.as_view(), name='transfer_payment'),
    path('verify-paystack-payment/<str:ref>', VerifyPaystackPayment.as_view(), name='verify_paystack_payment'),
    path('checkout', Checkout.as_view(), name='checkout'),
    path('cart', Cart.as_view(), name='cart'),
    path('cart-add-remove', CartAddRemove.as_view(), name='cart_add_remove'),
    path('cart-plus/<str:pk>', CartPlus.as_view(), name='cart_plus'),
    path('cart-minus/<str:pk>', CartMinus.as_view(), name='cart_minus'),
    path('cart-remove/<str:pk>', CartRemove.as_view(), name='cart_remove'),
    path('orders', Orders.as_view(), name='orders'),
    path('order-detail/<str:pk>', OrderDetail.as_view(), name='order_detail'),
    path('order-create/<str:pk>', OrderCreate.as_view(), name='order_create'),
    path('address', Address.as_view(), name='address'),
    path('settings', Settings.as_view(), name='settings'),
    path('settings/data', UserData.as_view(), name='user_data'),
    path('settings/password', UserPassword.as_view(), name='user_password'),
]
 
