from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.contrib.auth.hashers import make_password, check_password
from .forms import SignupForm
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from core import models
from main.views import Base


class Signup(Base):
	def get_request(self, request):
		logout(request)
		form = SignupForm()
		nav_text = 'Already have an account?'
		nav_link = reverse('login:signin')
		nav_value = 'Sign in'
		return (request, 'login/signup.html', {'form':form, 'nav_text': nav_text,
			'nav_link': nav_link, 'nav_value': nav_value})

	def post_request(self, request):
		form = SignupForm(request.POST)

		if form.is_valid():
			email = form.cleaned_data.get('email', '').strip().lower()
			name = form.cleaned_data.get('name', '').strip()
			number = form.cleaned_data.get('number', '').strip()
			password = form.cleaned_data.get('password', '').strip()

			user = models.User(email=email, name=name, number=number, password=password)
			user.is_active=False
			user.save()
			return redirect(reverse('login:confirm-token', kwargs={'user_id':user.id}))

		return (request, 'login/signup.html', {'form':form})


class ConfirmToken(Base):
	def get_request(self, request, user_id):
		base_url = request.scheme + '://' + request.get_host()

		user = models.User.objects.get(id=user_id)
		s = URLSafeTimedSerializer(settings.SECRET_KEY)
		token = s.dumps(user_id, salt='email-confirm')
		link = request.get_host() + reverse('login:confirm-email', kwargs={'user_id': user.id, 'token':token})
		html_body = get_template('login/template_confirm_email.html').render({'confirmation_email': link, 'base_url': base_url})
		msg = EmailMultiAlternatives('Confirmation email', f'Your confirmation link  {link}', 'nwaegunwaemmauel@gmail.com', [user.email])
		msg.attach_alternative(html_body, "text/html")
		msg.send()
		# messages.success(request, 'A confirmation email was sent.')
		return (request, 'login/status_msg.html', {
				'title': 'Confirm email', 
				'msg': 'Comfirmation email has been sent.', 
				'link': reverse("login:confirm-token", kwargs={"user_id": user_id}),
				'value': 'Resend',
			})


class ConfirmEmail(Base):
	def get_request(self, request, user_id, token):
		referer = request.META.get('HTTP_REFERER')

		try:
			s = URLSafeTimedSerializer(settings.SECRET_KEY)
			the_user_id = s.loads(token, salt='email-confirm', max_age=200000)
			user = models.User.objects.get(id=the_user_id)
			user.is_active = True
			user.save()
			return render(request, 'login/status_msg.html', {
				'title':'Email confirmed', 
				'msg':'Email confirmed you can now.', 
				'link': reverse('login:signin'),
				'value': 'Login',
			})
		except SignatureExpired:
			return (request, 'login/status_msg.html', {
				'title':'Token expired', 
				'msg':'This token has expired.', 
				'link': reverse("login:confirm-token", kwargs={"user_id": user_id}),
				'value': 'Get new one',
			})
