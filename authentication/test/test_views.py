import pdb

from .test_setup import TestStUp
from ..models import User


class TestView(TestStUp):
    def test_user_cant_register_without_data(self):
        response = self.client.post(self.register_url)
        self.assertEqual(response.status_code, 400)

    def test_user_can_register(self):
        response = self.client.post(self.register_url,
                                    data=self.user_data,
                                    format='json')

        self.assertEqual(response.data['email'],
                         self.user_data['email'],
                         msg="response's email and user's email arent same")

        self.assertEqual(response.data['username'],
                         self.user_data['username'])

        self.assertEqual(response.status_code, 201)

    def test_unverified_user_cant_login(self):
        self.client.post(self.register_url,
                         self.user_data,
                         format='json')
        res = self.client.post(self.login_url, self.user_data, format="json")
        self.assertEqual(res.status_code, 401)

    def test_verified_user_can_login(self):
        response = self.client.post(self.register_url,
                                    data=self.user_data,
                                    format='json')

        # Verify user manually
        user = User.objects.get(email=response.data['email'])
        user.is_verified = True
        user.save()

        response = self.client.post(self.login_url,
                                    self.user_data,
                                    format='json')
        self.assertEqual(response.status_code, 200)
