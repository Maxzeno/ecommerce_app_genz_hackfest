from django.core.management.base import BaseCommand
from django.utils import timezone
import random
from faker import Faker
from ...models import Product, SubCategory, User
from decouple import config


fake = Faker()

class Command(BaseCommand):
    help = 'Generate fake products'

    def add_arguments(self, parser):
        parser.add_argument('--num', help='Number to create', required=False)

    def handle(self, *args, **options):
        default = 3
        num = int(options.get('num') or default)
        for i in range(num):
            name = fake.name()
            email = fake.email()
            password = config('ADMIN_PASSWORDs', fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True))
            number = fake.phone_number()
            state = fake.state()
            address = fake.address()
            description = fake.text(max_nb_chars=1000)
            ordered = random.randint(0, 10)
            user = User.objects.create(
                name=name,
                email=email,
                password=password,
                number=number,
                state=state,
                address=address,
                description=description,
                ordered=ordered,
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created {i+1} user.'))
            