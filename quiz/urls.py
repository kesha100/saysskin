from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizListCreateAPIView, QuizSessionViewSet

router = DefaultRouter()

# router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'user-quizzes', QuizSessionViewSet, basename='userquiz')

urlpatterns = [
    path('', include(router.urls)),
    path('quizzes/', QuizListCreateAPIView.as_view(), name='quizzes' )
]