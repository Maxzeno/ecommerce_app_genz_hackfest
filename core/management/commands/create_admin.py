from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config

class Command(BaseCommand):
    help = 'Create an admin user with the custom user model'

    def handle(self, *args, **options):
        User = get_user_model()
        name = config('ADMIN_NAME')
        email = config('ADMIN_EMAIL')
        password = config('ADMIN_PASSWORD')
        found = User.objects.filter(email=email).first()
        if not found:
        	User.objects.create_superuser(name=name, email=email, password=password)
        	self.stdout.write(self.style.SUCCESS('Admin user created successfully!'))
        else:
        	self.stdout.write(self.style.SUCCESS('Admin user already exists!'))
        	if not found.check_password(password):
        		found.password = password
        		self.stdout.write(self.style.SUCCESS('Password updated!'))
        	if found.name != name:
        		found.name = name
        		self.stdout.write(self.style.SUCCESS('Name updated!'))
        	found.save()
        self.stdout.write(self.style.SUCCESS('Done with admin!'))
