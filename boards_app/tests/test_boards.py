from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from boards_app.models import Board

User = get_user_model()

class BoardTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="u1@ex.me", email="u1@ex.me", fullname="U 1", password="pw")
        self.user2 = User.objects.create_user(username="u2@ex.me", email="u2@ex.me", fullname="U 2", password="pw")
        self.user3 = User.objects.create_user(username="u3@ex.me", email="u3@ex.me", fullname="U 3", password="pw")
        
        self.board = Board.objects.create(name="Board 1", owner=self.user1)
        self.board.members.add(self.user1, self.user2)

        self.list_url = reverse('board-list')
        self.detail_url = reverse('board-detail', args=[self.board.id])

    def test_list_filters_by_membership(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data), 1)

        self.client.force_authenticate(user=self.user3)
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data), 0)

    def test_aggregation_counts(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_url)
        self.assertEqual(response.data[0]['members_count'], 2)

    def test_owner_protection_delete(self):
        self.client.force_authenticate(user=self.user2) # member, not owner
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.user1) # owner
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_email_check(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('email-check')
        response = self.client.get(f"{url}?email=u2@ex.me")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['fullname'], "U 2")

        response_nf = self.client.get(f"{url}?email=not@ex.me")
        self.assertEqual(response_nf.status_code, status.HTTP_404_NOT_FOUND)
