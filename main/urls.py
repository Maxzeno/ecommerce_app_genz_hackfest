from django.urls import path
from .views import Index, Products, ProductDetail, EmailSubscribe, ContactUs, WebhookVerifyPaystackPayment

app_name = 'main'

urlpatterns = [
    path('webhook-verify-paystack-payment', WebhookVerifyPaystackPayment.as_view(), name='webhook_verify_paystack_payment'),
    path('', Index.as_view(), name='index'),
    path('email-subscribe', EmailSubscribe.as_view(), name='email_subscribe'),
    path('contact-us', ContactUs.as_view(), name='contact_us'),
    path('products', Products.as_view(), name='products'),
    path('products/<str:pk>', ProductDetail.as_view(), name='product_detail'),
]
