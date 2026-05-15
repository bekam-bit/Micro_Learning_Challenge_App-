from django.db import transaction

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
    points = serializers.IntegerField(source='challenge.points')
    time_limit_minutes = serializers.IntegerField(source='challenge.time_limit_minutes')
    is_daily = serializers.BooleanField(read_only=True, default=True)

    # Allow writing to nested challenge fields
    challenge_data = serializers.DictField(write_only=True, required=False)
    challenge_id = serializers.PrimaryKeyRelatedField(
        queryset=Challenge.objects.all(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = DailyChallenge
        fields = [
            'id', 'challenge', 'date', 'title', 'description',
            'lesson', 'module', 'category', 'difficulty', 'points', 'time_limit_minutes', 'is_daily',
            'challenge_data', 'challenge_id', 'created_at'
        ]
        read_only_fields = ['challenge']

    def to_internal_value(self, data):
        for forbidden_owner in ('lesson', 'module', 'category'):
            if data.get(forbidden_owner) not in (None, ''):
                raise serializers.ValidationError({
                    forbidden_owner: 'Daily challenges cannot be bound to lesson/module/category.'
                })
        return super().to_internal_value(data)

    def create(self, validated_data):
        source_challenge = validated_data.pop('challenge_id', None)
        challenge_payload = validated_data.pop('challenge', {})
        challenge_data = validated_data.pop('challenge_data', {})

        if source_challenge and (challenge_payload or challenge_data):
            raise serializers.ValidationError({
                'challenge_id': 'Use either challenge_id or challenge fields, not both.'
            })

        if challenge_data:
            challenge_payload.update(challenge_data)

        if source_challenge is None and not challenge_payload:
            raise serializers.ValidationError({'challenge': 'Challenge payload is required.'})

        with transaction.atomic():
            if source_challenge is not None:
                challenge = Challenge.objects.create(
                    title=source_challenge.title,
                    description=source_challenge.description,
                    difficulty=source_challenge.difficulty,
                    points=source_challenge.points,
                    time_limit_minutes=source_challenge.time_limit_minutes,
                    is_daily=True,
                )

                source_questions = source_challenge.questions.all().order_by('order', 'id')
                ChallengeQuestion.objects.bulk_create([
                    ChallengeQuestion(
                        challenge=challenge,
                        question_text=question.question_text,
                        question_type=question.question_type,
                        options=question.options,
                        correct_options=question.correct_options,
                        correct_answer=question.correct_answer,
                        numeric_tolerance=question.numeric_tolerance,
                        explanation=question.explanation,
                        max_score=question.max_score,
                        order=question.order,
                    )
                    for question in source_questions
                ])
            else:
                challenge_payload['is_daily'] = True
                challenge = Challenge.objects.create(**challenge_payload)

            return DailyChallenge.objects.create(challenge=challenge, **validated_data)

    def update(self, instance, validated_data):
        challenge_payload = validated_data.pop('challenge', {})
        challenge_data = validated_data.pop('challenge_data', {})

        if challenge_data:
            challenge_payload.update(challenge_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if challenge_payload:
            for attr, value in challenge_payload.items():
                setattr(instance.challenge, attr, value)
            instance.challenge.is_daily = True
            instance.challenge.save()

        return instance


class DailyChallengeDetailSerializer(DailyChallengeSerializer, ChallengeDetailSerializer):
    questions = serializers.SerializerMethodField()

    class Meta(DailyChallengeSerializer.Meta):
        fields = DailyChallengeSerializer.Meta.fields + ['questions']

    def get_questions(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        queryset = obj.challenge.questions.all().order_by('order', 'id')

        if user and user.is_authenticated and getattr(user, 'role', None) == 'admin':
            return ChallengeQuestionAdminSerializer(queryset, many=True, context=self.context).data
        return ChallengeQuestionPublicSerializer(queryset, many=True, context=self.context).data


class DailyChallengeSubmissionSerializer(ChallengeSubmissionSerializer):
    pass
