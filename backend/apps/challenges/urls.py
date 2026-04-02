from django.urls import path

from .views import (
    ChallengeDetailView,
    ChallengeListCreateView,
    ChallengeProgressView,
    ChallengeQuestionDetailView,
    ChallengeQuestionListCreateView,
    ChallengeSubmitView,
    MyChallengeSubmissionsView,
)


urlpatterns = [
    path('', ChallengeListCreateView.as_view(), name='challenge_list_create'),
    path('<int:challenge_id>/questions/', ChallengeQuestionListCreateView.as_view(), name='challenge_question_list_create'),
    path('questions/<int:pk>/', ChallengeQuestionDetailView.as_view(), name='challenge_question_detail'),
    path('<int:challenge_id>/progress/', ChallengeProgressView.as_view(), name='challenge_progress'),
    path('<int:pk>/', ChallengeDetailView.as_view(), name='challenge_detail'),
    path('<int:challenge_id>/submit/', ChallengeSubmitView.as_view(), name='challenge_submit'),
    path('submissions/me/', MyChallengeSubmissionsView.as_view(), name='my_challenge_submissions'),
]
