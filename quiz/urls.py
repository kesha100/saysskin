from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuizViewSet, UserQuizViewSet, UserAnswerViewSet

router = DefaultRouter()

router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'user-quizzes', UserQuizViewSet, basename='userquiz')
router.register(r'user-answers', UserAnswerViewSet, basename='useranswer')

urlpatterns = [
    path('', include(router.urls)),
]