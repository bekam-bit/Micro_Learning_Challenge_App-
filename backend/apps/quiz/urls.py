from rest_framework.routers import DefaultRouter
from .views import (
    QuizAdminViewSet,
    QuestionAdminViewSet,
    AnswerAdminViewSet,
    QuizUserViewSet
)

router = DefaultRouter()

# Admin endpoints
router.register(r'admin/quizzes', QuizAdminViewSet, basename='admin-quizzes')
router.register(r'admin/questions', QuestionAdminViewSet, basename='admin-questions')
router.register(r'admin/answers', AnswerAdminViewSet, basename='admin-answers')

# User endpoints
router.register(r'quizzes', QuizUserViewSet, basename='user-quizzes')

urlpatterns = router.urls