from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from faker import Faker
import time
import os
import glob
import random
import shortuuid
from ...models import Product, SubCategory, User

fake = Faker()

class Command(BaseCommand):
    help = 'Generate fake products'

    def add_arguments(self, parser):
        parser.add_argument('--num', help='Number to create', required=False)

    def handle(self, *args, **options):
        default = 10
        num = int(options.get('num') or default)

        sub_categories = SubCategory.objects.all()
        if sub_categories:
            users = User.objects.all()

            # directory = 'static/assets/images/products'
            # path = os.path.join(settings.BASE_DIR, directory, '*.jpg')
            # jpg_files = glob.glob(path)


            # def create_image():
            #     # create a fake image file
            #     time.sleep(1)
            #     filepath = random.choice(jpg_files)
            #     random_txt = shortuuid.ShortUUID().random(length=8)
            #     filename = f'{random_txt}.jpg'
            #     file = open(filepath, 'rb')
            #     file_content = SimpleUploadedFile(filename, file.read())
            #     file.close()
            #     return file_content

            # images = [ create_image() for i in range(1, 5) ]

            for i in range(num):
                product = Product()
                product.name = fake.word()
                product.description = fake.text()
                product.state = fake.state()
                # product.image = fake.random_element(elements=images)
                product.sub_category = fake.random_element(elements=sub_categories)
                product.price = fake.pydecimal(left_digits=3, right_digits=2, positive=True)
                product.seller = fake.random_element(elements=users)
                product.ordered = fake.pyint(min_value=0, max_value=1000)
                product.is_approved = fake.pybool()
                product.data = {'size': fake.random_element(elements=[['S', 'M', 'L', 'XL'], [str(i) for i in range(40, 48)]])}
                product.save()

                self.stdout.write(self.style.SUCCESS(f'Successfully created {i+1} products.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Create category first'))
