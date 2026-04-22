from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, TaskCommentListView, TaskCommentDetailView

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('tasks/<int:task_id>/comments/', TaskCommentListView.as_view(), name='task-comments'),
    path('tasks/<int:task_id>/comments/<int:comment_id>/', TaskCommentDetailView.as_view(), name='task-comment-detail'),
    path('', include(router.urls)),
]
