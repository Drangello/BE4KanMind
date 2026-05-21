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

    def test_create_valid_task(self):
        self.client.force_authenticate(user=self.u_member1)
        data = {"title": "T2", "board": self.board.id, "assignee_id": self.u_member2.id, "reviewer_id": self.u_owner.id}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], "to-do")
        self.assertIn('fullname', response.data['assignee'])

    def test_create_invalid_assignee(self):
        self.client.force_authenticate(user=self.u_owner)
        data = {"title": "T2", "board": self.board.id, "assignee_id": self.u_outsider.id}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_invalid_reviewer(self):
        self.client.force_authenticate(user=self.u_owner)
        data = {"title": "T2", "board": self.board.id, "reviewer_id": self.u_outsider.id}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_non_member_forbidden(self):
        self.client.force_authenticate(user=self.u_outsider)
        data = {"title": "T2", "board": self.board.id}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_missing_board_not_found(self):
        self.client.force_authenticate(user=self.u_member1)
        data = {"title": "T2", "board": 4000}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_task(self):
        self.client.force_authenticate(user=self.u_member2)
        data = {"status": "in-progress"}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], "in-progress")

    def test_patch_forbid_board_change(self):
        self.client.force_authenticate(user=self.u_member1)
        b2 = Board.objects.create(title="B2", owner=self.u_owner)
        data = {"board": b2.id}
        response = self.client.patch(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_by_creator(self):
        self.client.force_authenticate(user=self.u_member1)
        self.assertEqual(self.client.delete(self.detail_url).status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_by_board_owner(self):
        t2 = Task.objects.create(title="T2", board=self.board, creator=self.u_member1)
        self.client.force_authenticate(user=self.u_owner)
        self.assertEqual(self.client.delete(reverse('task-detail', args=[t2.id])).status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_forbidden(self):
        self.client.force_authenticate(user=self.u_member2)
        self.assertEqual(self.client.delete(self.detail_url).status_code, status.HTTP_403_FORBIDDEN)

    def test_assigned_to_me(self):
        self.client.force_authenticate(user=self.u_member1)
        response = self.client.get(self.assign_url)
        self.assertEqual(len(response.data), 1)

    def test_reviewing(self):
        self.client.force_authenticate(user=self.u_member2)
        response = self.client.get(self.review_url)
        self.assertEqual(len(response.data), 1)

    def test_unauthorized_access(self):
        self.client.force_authenticate(user=self.u_outsider)
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_403_FORBIDDEN)
