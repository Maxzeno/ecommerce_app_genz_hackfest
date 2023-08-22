from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from ...models import Category, SubCategory


fake = Faker()

class Command(BaseCommand):
    help = 'Generate fake products'

    def add_arguments(self, parser):
        parser.add_argument('--num', help='Number to create', required=False)
        parser.add_argument('--num2', help='Number to create', required=False)

    def handle(self, *args, **options):
        default = 2
        num = int(options.get('num') or default)
        num2 = int(options.get('num2') or default)
        for i in range(num):
            category = Category.objects.create(
                name=fake.word(),
                description=fake.sentence(),
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created {i+1} category.'))
            for j in range(num2):
                SubCategory.objects.create(
                    name=fake.word(),
                    description=fake.sentence(),
                    category=category,
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created {j+1} sub category.'))




