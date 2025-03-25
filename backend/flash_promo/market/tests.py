from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from market.models import Store, Product


class StoreViewSetTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin", password="admin123"
        )
        self.client = APIClient()
        self.client.login(username="admin", password="admin123")  # Authenticate client
        self.store = Store.objects.create(
            name="Test Store", latitude=10.0, longitude=20.0
        )

    def test_get_stores(self):
        response = self.client.get("/api/market/stores/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Test Store")

    def test_create_store_as_admin(self):
        data = {"name": "New Store", "latitude": 15.0, "longitude": 25.0}
        response = self.client.post("/api/market/stores/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Store.objects.count(), 2)


class ProductViewSetTests(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin", password="admin123"
        )
        self.client = APIClient()
        self.client.login(username="admin", password="admin123")
        self.store = Store.objects.create(
            name="Test Store", latitude=10.0, longitude=20.0
        )
        self.product = Product.objects.create(
            name="Test Product", store=self.store, regular_price=100.0
        )

    def test_get_products(self):
        response = self.client.get("/api/market/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Test Product")
