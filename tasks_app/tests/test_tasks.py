from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from boards_app.models import Board
from tasks_app.models import Task

User = get_user_model()

class TaskTests(APITestCase):
    def setUp(self):
        self.u_owner = User.objects.create_user(username="owner", email="o@ex.me", fullname="Owner")
        self.u_member1 = User.objects.create_user(username="m1", email="m1@ex.me", fullname="M1")
        self.u_member2 = User.objects.create_user(username="m2", email="m2@ex.me", fullname="M2")
        self.u_outsider = User.objects.create_user(username="out", email="out@ex.me", fullname="Out")

        self.board = Board.objects.create(title="B1", owner=self.u_owner)
        self.board.members.add(self.u_owner, self.u_member1, self.u_member2)

        self.task1 = Task.objects.create(
            title="T1", board=self.board, creator=self.u_member1,
            assignee=self.u_member1, reviewer=self.u_member2
        )
        self.list_url = reverse('task-list')
        self.assign_url = reverse('task-assigned-to-me')
        self.review_url = reverse('task-reviewing')
        self.detail_url = reverse('task-detail', args=[self.task1.id])

    def test_create_task_valid(self):
        self.client.force_authenticate(user=self.u_member1)
        data = {"title": "T2", "board": self.board.id, "assignee": self.u_member2.id}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['creator'], self.u_member1.id)

    def test_create_invalid_assignee(self):
        self.client.force_authenticate(user=self.u_owner)
        data = {"title": "T2", "board": self.board.id, "assignee": self.u_outsider.id}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_patch_forbid_board_change(self):
        self.client.force_authenticate(user=self.u_member1)
        b2 = Board.objects.create(title="B2", owner=self.u_owner)
        data = {"board": b2.id}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_permissions(self):
        # Outsider forbidden entirely
        self.client.force_authenticate(user=self.u_outsider)
        self.assertEqual(self.client.delete(self.detail_url).status_code, status.HTTP_404_NOT_FOUND)
        
        # Member2 (reviewer, but not creator nor owner) forbidden
        self.client.force_authenticate(user=self.u_member2)
        self.assertEqual(self.client.delete(self.detail_url).status_code, status.HTTP_403_FORBIDDEN)
        
        # Creator allowed
        self.client.force_authenticate(user=self.u_member1)
        self.assertEqual(self.client.delete(self.detail_url).status_code, status.HTTP_204_NO_CONTENT)

        # Owner allowed
        t2 = Task.objects.create(title="T2", board=self.board, creator=self.u_member1)
        self.client.force_authenticate(user=self.u_owner)
        self.assertEqual(self.client.delete(reverse('task-detail', args=[t2.id])).status_code, status.HTTP_204_NO_CONTENT)

    def test_assigned_to_me(self):
        self.client.force_authenticate(user=self.u_member1)
        response = self.client.get(self.assign_url)
        self.assertEqual(len(response.data), 1)

    def test_reviewing(self):
        self.client.force_authenticate(user=self.u_member2)
        response = self.client.get(self.review_url)
        self.assertEqual(len(response.data), 1)
