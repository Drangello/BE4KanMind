from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from boards_app.models import Board
from tasks_app.models import Task, Comment

User = get_user_model()

class CommentTests(APITestCase):
    def setUp(self):
        self.u_owner = User.objects.create_user(username="owner", email="o@ex.me", fullname="Owner")
        self.u_member = User.objects.create_user(username="m1", email="m1@ex.me", fullname="M1")
        self.u_outsider = User.objects.create_user(username="out", email="out@ex.me", fullname="Out")

        self.board = Board.objects.create(title="B1", owner=self.u_owner)
        self.board.members.add(self.u_member)

        self.task1 = Task.objects.create(
            title="T1", board=self.board, creator=self.u_owner
        )
        self.comment1 = Comment.objects.create(
            task=self.task1, author=self.u_owner, content="C1"
        )
        self.list_url = reverse('comment-list')
        self.detail_url = reverse('comment-detail', args=[self.comment1.id])

    def test_list_comments_ordered(self):
        Comment.objects.create(task=self.task1, author=self.u_member, content="C2")
        self.client.force_authenticate(user=self.u_owner)
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['content'], "C1")
        self.assertEqual(response.data[1]['content'], "C2")

    def test_create_comment(self):
        self.client.force_authenticate(user=self.u_member)
        data = {"task": self.task1.id, "content": "New comment"}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['author'], self.u_member.fullname)

    def test_create_forbidden_for_outsider(self):
        self.client.force_authenticate(user=self.u_outsider)
        data = {"task": self.task1.id, "content": "Malicious"}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_comment_by_author(self):
        self.client.force_authenticate(user=self.u_owner)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_comment_forbidden(self):
        self.client.force_authenticate(user=self.u_member) # member, but not author
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_filters_by_board_access(self):
        self.client.force_authenticate(user=self.u_outsider)
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data), 0)

    def test_filter_by_task(self):
        task2 = Task.objects.create(title="T2", board=self.board, creator=self.u_owner)
        Comment.objects.create(task=task2, author=self.u_owner, content="C3")
        self.client.force_authenticate(user=self.u_owner)
        response = self.client.get(f"{self.list_url}?task={self.task1.id}")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['content'], "C1")
