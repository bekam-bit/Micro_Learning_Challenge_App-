from django.utils import timezone

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.challenges.models import ChallengeQuestion
from apps.challenges.views import (
    ChallengeDetailView,
    ChallengeListCreateView,
    ChallengeProgressView,
    ChallengeQuestionDetailView,
    ChallengeQuestionListCreateView,
    ChallengeSubmitView,
    MyChallengeSubmissionsView,
)

from .models import DailyChallenge
from .serializers import DailyChallengeDetailSerializer, DailyChallengeSerializer


class DailyChallengeListCreateView(ChallengeListCreateView):
    is_daily_scope = True
    cache_namespace = 'daily_challenges'
    queryset = DailyChallenge.objects.select_related('lesson', 'module', 'category').all()
    serializer_class = DailyChallengeSerializer

    def get_base_queryset(self):
        return DailyChallenge.objects.select_related('lesson', 'module', 'category').all()

    def get_queryset(self):
        queryset = self.get_base_queryset()

        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        date_value = self.request.query_params.get('date')
        if date_value:
            queryset = queryset.filter(date=date_value)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)

        sort_by = self.request.query_params.get('sort_by', '-date')
        allowed_sort_fields = {'date', '-date', 'title', '-title', 'points', '-points', 'created_at', '-created_at'}
        if sort_by not in allowed_sort_fields:
            sort_by = '-date'

        return queryset.order_by(sort_by, 'id')


class DailyChallengeTodayView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        date_value = request.query_params.get('date')
        if date_value:
            challenge = DailyChallenge.objects.filter(date=date_value).first()
        else:
            challenge = DailyChallenge.objects.filter(date=timezone.localdate()).first()

        if challenge is None:
            return Response({'detail': 'No daily challenge found for the requested date.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = DailyChallengeDetailSerializer(challenge, context={'request': request})
        return Response(serializer.data)

class DailyChallengeDetailView(ChallengeDetailView):
    is_daily_scope = True
    cache_namespace = 'daily_challenges'

    def get_base_queryset(self):
        return DailyChallenge.objects.select_related('lesson', 'module', 'category').all()

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return DailyChallengeDetailSerializer
        return DailyChallengeSerializer


class DailyChallengeQuestionListCreateView(ChallengeQuestionListCreateView):
    is_daily_scope = True
    cache_namespace = 'daily_challenges'


class DailyChallengeQuestionDetailView(ChallengeQuestionDetailView):
    queryset = ChallengeQuestion.objects.select_related('challenge').filter(challenge__is_daily=True)
    cache_namespace = 'daily_challenges'


class DailyChallengeProgressView(ChallengeProgressView):
    is_daily_scope = True


class DailyChallengeSubmitView(ChallengeSubmitView):
    is_daily_scope = True


class MyDailyChallengeSubmissionsView(MyChallengeSubmissionsView):
    is_daily_scope = True
