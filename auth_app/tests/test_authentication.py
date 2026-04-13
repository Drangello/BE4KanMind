from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class RegistrationTests(APITestCase):
    """
    Test suite for user registration.
    """
    def setUp(self):
        self.url = reverse('registration')

    def test_registration_success(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword123!",
            "repeated_password": "StrongPassword123!"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)

    def test_registration_password_mismatch(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPassword123!",
            "repeated_password": "WrongPassword!"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_registration_missing_fields(self):
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(APITestCase):
    """
    Test suite for user login.
    """
    def setUp(self):
        self.url = reverse('login')
        self.user = User.objects.create_user(
            username="loginuser",
            email="login@example.com",
            password="LoginPassword123!"
        )

    def test_login_success(self):
        data = {
            "username": "loginuser",
            "password": "LoginPassword123!"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_login_failure(self):
        data = {
            "username": "loginuser",
            "password": "WrongPassword!"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
