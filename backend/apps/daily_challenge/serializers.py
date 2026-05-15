from rest_framework import serializers  # type: ignore[import]

from apps.challenges.models import Challenge, ChallengeQuestion
from apps.challenges.serializers import (
    ChallengeDetailSerializer,
    ChallengeQuestionAdminSerializer,
    ChallengeQuestionPublicSerializer,
    ChallengeSerializer,
    ChallengeSubmissionSerializer,
)

from .models import DailyChallenge

class DailyChallengeSerializer(serializers.ModelSerializer):
    # Include fields from the related Challenge model
    title = serializers.CharField(source='challenge.title')
    description = serializers.CharField(source='challenge.description')
    lesson = serializers.PrimaryKeyRelatedField(source='challenge.lesson', read_only=True)
    module = serializers.PrimaryKeyRelatedField(source='challenge.module', read_only=True)
    category = serializers.PrimaryKeyRelatedField(source='challenge.category', read_only=True)
    difficulty = serializers.ChoiceField(source='challenge.difficulty', choices=Challenge.DIFFICULTY_CHOICES)
    is_daily = serializers.BooleanField(read_only=True, default=True)
    
    # Allow writing to nested challenge fields
    challenge_data = serializers.DictField(write_only=True, required=False)

    class Meta:
        model = DailyChallenge
        fields = [
            'id', 'challenge', 'date', 'title', 'description', 
            'lesson', 'module', 'category', 'difficulty', 'is_daily', 
            'challenge_data', 'created_at'
        ]

    def to_internal_value(self, data):
        # Strip out read-only proxy fields if they are sent in the request
        # to prevent validation errors, relying on challenge_data or challenge ID instead
        ignore_fields = ['title', 'description', 'lesson', 'module', 'category', 'difficulty', 'is_daily']
        for field in ignore_fields:
            data.pop(field, None)
        return super().to_internal_value(data)

    def create(self, validated_data):
        challenge_data = validated_data.pop('challenge_data', {})
        
        # If challenge_data is provided, create the underlying Challenge first
        if challenge_data:
            challenge = Challenge.objects.create(
                is_daily=True,
                **challenge_data
            )
            validated_data['challenge'] = challenge
        
        return super().create(validated_data)


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
