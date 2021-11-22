from rest_framework.test import APITestCase
from django.urls import reverse
from faker import Faker


class TestStUp(APITestCase):

    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        fake = Faker()
        self.user_data = {
            'email': fake.email(),
            'username': fake.email().split('@')[0],
            'password': fake.password(),
        }

        return super().setUp()

    def tearDown(self):
        return super().tearDown()
