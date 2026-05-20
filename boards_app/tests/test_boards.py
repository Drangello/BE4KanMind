from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from boards_app.models import Board
from tasks_app.models import Task

User = get_user_model()

class BoardTests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(email="u1@ex.me", username="u1", fullname="Owner")
        self.user2 = User.objects.create_user(email="u2@ex.me", username="u2", fullname="Member")
        self.user3 = User.objects.create_user(email="u3@ex.me", username="u3", fullname="Other")
        
        self.board = Board.objects.create(title="Board 1", owner=self.user1)
        self.board.members.add(self.user1, self.user2)

        self.task1 = Task.objects.create(title="T1", board=self.board, status="to-do", priority="high", creator=self.user1)
        self.task2 = Task.objects.create(title="T2", board=self.board, status="in-progress", creator=self.user1)

        self.list_url = reverse('board-list')
        self.detail_url = reverse('board-detail', args=[self.board.id])

    def test_create_board(self):
        self.client.force_authenticate(user=self.user1)
        data = {"title": "New Board", "members": [self.user2.id]}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        board = Board.objects.get(id=response.data['id'])
        self.assertEqual(board.owner, self.user1)
        self.assertIn(self.user1, board.members.all())
        self.assertIn(self.user2, board.members.all())

    def test_list_boards_filtered_by_user(self):
        self.client.force_authenticate(user=self.user1)
        resp1 = self.client.get(self.list_url)
        self.assertEqual(len(resp1.data), 1)
        self.assertEqual(resp1.data[0]['member_count'], 2)
        self.assertEqual(resp1.data[0]['ticket_count'], 2)
        self.assertEqual(resp1.data[0]['tasks_to_do_count'], 1)

        self.client.force_authenticate(user=self.user3)
        resp3 = self.client.get(self.list_url)
        self.assertEqual(len(resp3.data), 0)

    def test_retrieve_board_detail_with_tasks(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tasks', response.data)
        self.assertEqual(len(response.data['tasks']), 2)
        self.assertEqual(response.data['tasks'][0]['title'], "T1")

    def test_update_board_members_replacement(self):
        self.client.force_authenticate(user=self.user1)
        data = {"title": "Updated", "members": [self.user3.id]}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.board.refresh_from_db()
        self.assertEqual(self.board.title, "Updated")
        members = self.board.members.all()
        self.assertIn(self.user3, members)
        self.assertIn(self.user1, members)
        self.assertNotIn(self.user2, members)

    def test_delete_only_owner_allowed(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.user1)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauthorized_access(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
