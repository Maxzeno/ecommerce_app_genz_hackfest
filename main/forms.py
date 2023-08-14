from django import forms


class EmailForm(forms.Form):
	email = forms.EmailField(required=False, label='', max_length=100,  widget=forms.EmailInput(attrs={
		'placeholder':'Email Address', 'class': 'form-control', 'id': 'emailAddress'
		}))


class ContactUsForm(forms.Form):
	email = forms.EmailField(required=False, label='', max_length=100,  widget=forms.EmailInput(attrs={
		'placeholder':'Email Address', 'class': 'form-control', 'id': 'emailAddress'
		}))

	message = forms.CharField(required=False, label='', max_length=1000,  widget=forms.Textarea(attrs={
		'rows': 5, 'cols': 40, 'placeholder':'Message', 'class': 'form-control'
		}))

	def clean_email(self):
		email = self.cleaned_data.get('email')
		if not email or len(email) == 0:
			raise forms.ValidationError('Email is required')
		return email
		
	def clean_message(self):
		message = self.cleaned_data.get('message')
		if not message or len(message) == 0:
			raise forms.ValidationError('Message is required')
		return message
