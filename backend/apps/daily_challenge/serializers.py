from rest_framework import serializers

from apps.challenges.models import ChallengeQuestion
from apps.challenges.serializers import (
    ChallengeDetailSerializer,
    ChallengeQuestionAdminSerializer,
    ChallengeQuestionPublicSerializer,
    ChallengeSerializer,
    ChallengeSubmissionSerializer,
)

from .models import DailyChallenge


class DailyChallengeSerializer(ChallengeSerializer):
    class Meta(ChallengeSerializer.Meta):
        model = DailyChallenge
        fields = [
            'id',
            'is_daily',
            'date',
            'title',
            'description',
            'difficulty',
            'points',
            'time_limit_minutes',
            'created_at',
            'scope',
            'scope_display',
            'lesson',
            'module',
            'category',
        ]
        read_only_fields = ['id', 'is_daily', 'scope', 'scope_display']

    def validate(self, attrs):
        attrs = dict(attrs)
        attrs['is_daily'] = True

        lesson = attrs.get('lesson', getattr(self.instance, 'lesson', None) if self.instance else None)
        module = attrs.get('module', getattr(self.instance, 'module', None) if self.instance else None)
        category = attrs.get('category', getattr(self.instance, 'category', None) if self.instance else None)
        if lesson or module or category:
            raise serializers.ValidationError('Daily challenges cannot be bound to lesson, module, or category.')

        if not attrs.get('date') and not getattr(self.instance, 'date', None):
            raise serializers.ValidationError({'date': 'Daily challenge date is required.'})

        return attrs


class DailyChallengeDetailSerializer(DailyChallengeSerializer, ChallengeDetailSerializer):
    questions = serializers.SerializerMethodField()

    class Meta(DailyChallengeSerializer.Meta):
        fields = DailyChallengeSerializer.Meta.fields + ['questions']

    def get_questions(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        queryset = obj.questions.all().order_by('order', 'id')

        if user and user.is_authenticated and getattr(user, 'role', None) == 'admin':
            return ChallengeQuestionAdminSerializer(queryset, many=True, context=self.context).data
        return ChallengeQuestionPublicSerializer(queryset, many=True, context=self.context).data


class DailyChallengeSubmissionSerializer(ChallengeSubmissionSerializer):
    pass
