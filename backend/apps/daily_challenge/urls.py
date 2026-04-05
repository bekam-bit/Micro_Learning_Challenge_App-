from django.urls import path

from .views import (
    DailyChallengeDetailView,
    DailyChallengeListCreateView,
    DailyChallengeProgressView,
    DailyChallengeQuestionDetailView,
    DailyChallengeQuestionListCreateView,
    DailyChallengeSubmitView,
    DailyChallengeTodayView,
    MyDailyChallengeSubmissionsView,
)


urlpatterns = [
    path('', DailyChallengeListCreateView.as_view(), name='daily_challenge_list_create'),
    path('today/', DailyChallengeTodayView.as_view(), name='daily_challenge_today'),
    path('<int:challenge_id>/questions/', DailyChallengeQuestionListCreateView.as_view(), name='daily_challenge_question_list_create'),
    path('questions/<int:pk>/', DailyChallengeQuestionDetailView.as_view(), name='daily_challenge_question_detail'),
    path('<int:challenge_id>/progress/', DailyChallengeProgressView.as_view(), name='daily_challenge_progress'),
    path('<int:pk>/', DailyChallengeDetailView.as_view(), name='daily_challenge_detail'),
    path('<int:challenge_id>/submit/', DailyChallengeSubmitView.as_view(), name='daily_challenge_submit'),
    path('submissions/me/', MyDailyChallengeSubmissionsView.as_view(), name='my_daily_challenge_submissions'),
]
