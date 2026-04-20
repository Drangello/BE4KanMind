from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class EmailCheckTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="test@ex.me", username="test", fullname="Test User")
        self.url = reverse('email-check')
        self.client.force_authenticate(user=self.user)

    def test_email_check_success(self):
        response = self.client.get(f"{self.url}?email=test@ex.me")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['fullname'], "Test User")
        self.assertEqual(response.data['id'], self.user.id)

    def test_email_check_not_found(self):
        response = self.client.get(f"{self.url}?email=nope@ex.me")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_email_check_missing_param(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
