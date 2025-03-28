from django.core.management.base import BaseCommand
from users.models import UserSegment, ClientProfile
from market.models import Store, Product
from django.contrib.auth.models import User
from flash_promo import settings
from datetime import datetime, timedelta
from promotions.models import FlashPromo
from decimal import Decimal


class Command(BaseCommand):
    help = "Populate the database with test data"

    def handle(self, *args, **kwargs):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL,
                password=settings.ADMIN_PASSWORD,
            )
            self.stdout.write(
                self.style.SUCCESS("Superuser 'admin' created successfully!")
            )
        else:
            self.stdout.write(self.style.WARNING("Superuser 'admin' already exists."))

        # Create User Segments
        segment1 = UserSegment.objects.create(
            name="Segment A", description="Test Segment A"
        )
        segment2 = UserSegment.objects.create(
            name="Segment B", description="Test Segment B"
        )

        # Create Users and Client Profiles
        users = []
        for i in range(1, 11):  # Create 10 users
            user = User.objects.create_user(
                username=f"user{i}", password=f"password{i}"
            )

            # Asign users randomdly near stores
            if i % 3 == 1:  # Users near Store A
                latitude, longitude = 40.7128 + 0.01, -74.0060 + 0.01
            elif i % 3 == 2:  # Users near Store B
                latitude, longitude = 34.0522 + 0.01, -118.2437 - 0.01
            else:  # Users near Store C
                latitude, longitude = 37.7749 - 0.01, -122.4194 + 0.01

            profile = ClientProfile.objects.create(
                user=user, latitude=latitude, longitude=longitude
            )
            profile.segments.add(segment1 if i % 2 == 0 else segment2)
            users.append(user)

        # Create Stores
        store1 = Store.objects.create(
            name="Store A", latitude=40.7128, longitude=-74.0060
        )
        store2 = Store.objects.create(
            name="Store B", latitude=34.0522, longitude=-118.2437
        )
        store3 = Store.objects.create(
            name="Store C", latitude=37.7749, longitude=-122.4194
        )

        stores = [store1, store2, store3]

        # Create Products
        products = [
            "Laptop",
            "Smartphone",
            "Tablet",
            "Smartwatch",
            "Headphones",
            "Keyboard",
            "Mouse",
            "Monitor",
            "Printer",
            "Router",
            "Webcam",
            "External Hard Drive",
            "USB Flash Drive",
            "Graphics Card",
            "Processor",
            "Motherboard",
            "RAM",
            "Power Supply",
            "Cooling Fan",
            "VR Headset",
        ]

        for i, product_name in enumerate(products, start=1):
            Product.objects.create(
                name=product_name,
                store=stores[i % 3],  # Distribute products across the 3 stores
                regular_price=50.00 + i * 10.00,  # Increment price for variety
            )

        for i, product in enumerate(Product.objects.all()[:10], start=1):
            end_time = datetime.now() - timedelta(days=i)
            start_time = end_time - timedelta(hours=4)
            promo_price = product.regular_price * Decimal(0.8)
            flash_promo = FlashPromo.objects.create(
                product=product,
                promo_price=promo_price,
                start_time=start_time,
                end_time=end_time,
                is_active=True if i % 2 == 0 else False,
            )
            flash_promo.segments.add(segment1 if i % 2 == 0 else segment2)

        self.stdout.write(self.style.SUCCESS("Test data successfully created!"))
