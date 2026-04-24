from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BoardViewSet, EmailCheckView

router = DefaultRouter()
router.register(r'boards', BoardViewSet, basename='board')

urlpatterns = [
    path('', include(router.urls)),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
]
