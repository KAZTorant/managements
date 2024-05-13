from django.core.management.base import BaseCommand
from faker import Faker
from django.utils import timezone
import random
from apps.orders.models import Order
from apps.tables.models import Table
from apps.users.models import User

class Command(BaseCommand):
    help = 'Fills the database with dummy data for orders'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--number', type=int, help='Number of orders to create', default=50)

    def handle(self, *args, **options):
        fake = Faker()  # Create an instance of Faker to generate fake data
        num_orders = options['number']
        user_ids = list(User.objects.values_list('id', flat=True))
        table_ids = list(Table.objects.values_list('id', flat=True))

        for _ in range(num_orders):
            # Use Faker to generate a random datetime within the past year
            random_date = fake.date_time_between(start_date='-365d', end_date='now')
            random_date = timezone.make_aware(random_date)  # Ensure the datetime is timezone-aware

            order = Order(
                table_id=random.choice(table_ids),
                is_paid=random.choice([True, False]),
                is_check_printed=random.choice([True, False]),
                waitress_id=random.choice(user_ids) if user_ids else None,
                total_price=random.uniform(10.0, 100.0),
                created_at=random_date  # Use the randomly generated datetime
            )
            order.save()
            self.stdout.write(f'Created order {order.id}')
