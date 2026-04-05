import json

from rest_framework import serializers

from .models import (
    Challenge,
    ChallengeAttempt,
    ChallengeAttemptAnswer,
    ChallengeQuestion,
    ChallengeSubmission,
)


class ChallengeSerializer(serializers.ModelSerializer):
    scope = serializers.SerializerMethodField()
    scope_display = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = [
            'id',
            'is_daily',
            'title',
            'description',
            'difficulty',
            'points',
            'time_limit_minutes',
            'created_at',
            'lesson',
            'module',
            'category',
            'scope',
            'scope_display',
        ]
        read_only_fields = ['id', 'is_daily', 'scope', 'scope_display']

    def get_scope(self, obj):
        return obj.get_scope()

    def get_scope_display(self, obj):
        return obj.get_scope_display()

    def validate(self, attrs):
        if attrs.get('is_daily', False):
            raise serializers.ValidationError('Daily challenges must be created through the daily challenge endpoint.')

        lesson = attrs.get('lesson', getattr(self.instance, 'lesson', None) if self.instance else None)
        module = attrs.get('module', getattr(self.instance, 'module', None) if self.instance else None)
        category = attrs.get('category', getattr(self.instance, 'category', None) if self.instance else None)

        owners_count = sum(bool(owner) for owner in (lesson, module, category))
        if owners_count != 1:
            raise serializers.ValidationError('A challenge must belong to exactly one owner: lesson, module, or category.')

        return attrs


class ChallengeDetailSerializer(ChallengeSerializer):
    questions = serializers.SerializerMethodField()

    class Meta(ChallengeSerializer.Meta):
        fields = ChallengeSerializer.Meta.fields + ['questions']

    def get_questions(self, obj):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        queryset = obj.questions.all().order_by('order', 'id')

        if user and user.is_authenticated and getattr(user, 'role', None) == 'admin':
            return ChallengeQuestionAdminSerializer(queryset, many=True, context=self.context).data
        return ChallengeQuestionPublicSerializer(queryset, many=True, context=self.context).data


class ChallengeSubmissionSerializer(serializers.ModelSerializer):
    challenge_title = serializers.CharField(source='challenge.title', read_only=True)
    is_within_time_limit = serializers.BooleanField(source='attempt.is_within_time_limit', read_only=True)
    challenge_deadline_at = serializers.DateTimeField(source='attempt.deadline_at', read_only=True)
    completion_time_seconds = serializers.SerializerMethodField()
    submission_timing_status = serializers.SerializerMethodField()

    class Meta:
        model = ChallengeSubmission
        fields = [
            'id',
            'challenge',
            'challenge_title',
            'user',
            'attempt',
            'response_text',
            'status',
            'score',
            'submitted_at',
            'updated_at',
            'is_within_time_limit',
            'challenge_deadline_at',
            'completion_time_seconds',
            'submission_timing_status',
        ]
        read_only_fields = ['id', 'challenge', 'challenge_title', 'user', 'status', 'score', 'submitted_at', 'updated_at']

    def get_completion_time_seconds(self, obj):
        if not obj.attempt or not obj.attempt.started_at or not obj.attempt.submitted_at:
            return None
        delta = obj.attempt.submitted_at - obj.attempt.started_at
        return int(delta.total_seconds())

    def get_submission_timing_status(self, obj):
        if not obj.attempt or not obj.attempt.is_submitted:
            return 'not_submitted'
        return 'on_time' if obj.attempt.is_within_time_limit else 'late'


class ChallengeSubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChallengeSubmission
        fields = ['response_text']


class ChallengeQuestionAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChallengeQuestion
        fields = [
            'id',
            'challenge',
            'question_text',
            'question_type',
            'options',
            'correct_options',
            'correct_answer',
            'numeric_tolerance',
            'explanation',
            'max_score',
            'order',
        ]
        read_only_fields = ['id', 'challenge']

    def validate(self, attrs):
        question_type = attrs.get('question_type', getattr(self.instance, 'question_type', ChallengeQuestion.TYPE_SHORT_TEXT_STRICT))
        options = attrs.get('options', getattr(self.instance, 'options', []))
        correct_options = attrs.get('correct_options', getattr(self.instance, 'correct_options', []))
        correct_answer = attrs.get('correct_answer', getattr(self.instance, 'correct_answer', ''))
        numeric_tolerance = attrs.get('numeric_tolerance', getattr(self.instance, 'numeric_tolerance', 0))

        if question_type in {ChallengeQuestion.TYPE_SINGLE_CHOICE, ChallengeQuestion.TYPE_MULTIPLE_CHOICE}:
            if not options:
                raise serializers.ValidationError({'options': 'Options are required for choice question types.'})

        if question_type == ChallengeQuestion.TYPE_SINGLE_CHOICE:
            if not correct_answer:
                raise serializers.ValidationError({'correct_answer': 'Single choice requires a correct_answer value.'})
            if correct_answer not in options:
                raise serializers.ValidationError({'correct_answer': 'correct_answer must be one of the provided options.'})

        if question_type == ChallengeQuestion.TYPE_MULTIPLE_CHOICE:
            if not isinstance(correct_options, list) or not correct_options:
                raise serializers.ValidationError({'correct_options': 'Multiple choice requires a non-empty correct_options list.'})
            invalid_options = [value for value in correct_options if value not in options]
            if invalid_options:
                raise serializers.ValidationError({'correct_options': 'Each correct option must be present in options.'})

        if question_type == ChallengeQuestion.TYPE_TRUE_FALSE:
            if correct_answer.lower() not in {'true', 'false'}:
                raise serializers.ValidationError({'correct_answer': 'True/False questions require correct_answer to be true or false.'})

        if question_type == ChallengeQuestion.TYPE_NUMERIC:
            try:
                float(correct_answer)
            except (TypeError, ValueError):
                raise serializers.ValidationError({'correct_answer': 'Numeric questions require correct_answer to be a number.'})
            if numeric_tolerance < 0:
                raise serializers.ValidationError({'numeric_tolerance': 'numeric_tolerance must be >= 0.'})

        return attrs


class ChallengeQuestionPublicSerializer(serializers.ModelSerializer):
    answer_format = serializers.SerializerMethodField()

    class Meta:
        model = ChallengeQuestion
        fields = ['id', 'challenge', 'question_text', 'question_type', 'options', 'max_score', 'order', 'answer_format']
        read_only_fields = ['id']

    def get_answer_format(self, obj):
        if obj.question_type == ChallengeQuestion.TYPE_SINGLE_CHOICE:
            return {
                'field': 'answer_text',
                'type': 'string',
                'description': 'Send exactly one selected option value.',
            }
        if obj.question_type == ChallengeQuestion.TYPE_MULTIPLE_CHOICE:
            return {
                'field': 'answer_options',
                'type': 'string[]',
                'description': 'Send selected option values as an array. Order does not matter.',
            }
        if obj.question_type == ChallengeQuestion.TYPE_TRUE_FALSE:
            return {
                'field': 'answer_boolean',
                'type': 'boolean',
                'description': 'Send true or false.',
            }
        if obj.question_type == ChallengeQuestion.TYPE_NUMERIC:
            return {
                'field': 'answer_number',
                'type': 'number',
                'description': 'Send a numeric value. Tolerance is applied on backend.',
            }
        return {
            'field': 'answer_text',
            'type': 'string',
            'description': 'Send plain text answer (strict normalized match).',
        }


class ChallengeAnswerInputSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer_text = serializers.CharField(allow_blank=True, required=False, default='')
    answer_options = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    answer_number = serializers.FloatField(required=False, allow_null=True)
    answer_boolean = serializers.BooleanField(required=False, allow_null=True)


class ChallengeProgressUpsertSerializer(serializers.Serializer):
    answers = ChallengeAnswerInputSerializer(many=True)


class ChallengeAttemptAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    question_type = serializers.CharField(source='question.question_type', read_only=True)
    submitted_answer = serializers.SerializerMethodField()

    class Meta:
        model = ChallengeAttemptAnswer
        fields = ['question', 'question_text', 'question_type', 'submitted_answer']
        read_only_fields = ['question_text']

    def get_submitted_answer(self, obj):
        if obj.question.question_type == ChallengeQuestion.TYPE_MULTIPLE_CHOICE:
            try:
                return json.loads(obj.answer_text or '[]')
            except json.JSONDecodeError:
                return []
        if obj.question.question_type == ChallengeQuestion.TYPE_TRUE_FALSE:
            normalized = (obj.answer_text or '').strip().lower()
            if normalized in {'true', 'false'}:
                return normalized == 'true'
            return None
        if obj.question.question_type == ChallengeQuestion.TYPE_NUMERIC:
            try:
                return float(obj.answer_text)
            except (TypeError, ValueError):
                return None
        return obj.answer_text


class ChallengeSubmissionAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.question_text', read_only=True)
    question_type = serializers.CharField(source='question.question_type', read_only=True)
    correct_answer_value = serializers.SerializerMethodField()
    submitted_answer = serializers.SerializerMethodField()
    explanation = serializers.CharField(source='question.explanation', read_only=True)

    class Meta:
        model = ChallengeAttemptAnswer
        fields = ['question', 'question_text', 'question_type', 'submitted_answer', 'correct_answer_value', 'score', 'explanation']
        read_only_fields = fields

    def get_submitted_answer(self, obj):
        if obj.question.question_type == ChallengeQuestion.TYPE_MULTIPLE_CHOICE:
            try:
                return json.loads(obj.answer_text or '[]')
            except json.JSONDecodeError:
                return []
        if obj.question.question_type == ChallengeQuestion.TYPE_TRUE_FALSE:
            normalized = (obj.answer_text or '').strip().lower()
            if normalized in {'true', 'false'}:
                return normalized == 'true'
            return None
        if obj.question.question_type == ChallengeQuestion.TYPE_NUMERIC:
            try:
                return float(obj.answer_text)
            except (TypeError, ValueError):
                return None
        return obj.answer_text

    def get_correct_answer_value(self, obj):
        question = obj.question
        if question.question_type == ChallengeQuestion.TYPE_MULTIPLE_CHOICE:
            return question.correct_options
        if question.question_type == ChallengeQuestion.TYPE_TRUE_FALSE:
            return question.correct_answer.strip().lower() == 'true'
        if question.question_type == ChallengeQuestion.TYPE_NUMERIC:
            try:
                return float(question.correct_answer)
            except (TypeError, ValueError):
                return question.correct_answer
        return question.correct_answer


class ChallengeAttemptSerializer(serializers.ModelSerializer):
    challenge_title = serializers.CharField(source='challenge.title', read_only=True)
    answers = ChallengeAttemptAnswerSerializer(many=True, read_only=True)
    completion_time_seconds = serializers.SerializerMethodField()
    submission_timing_status = serializers.SerializerMethodField()

    class Meta:
        model = ChallengeAttempt
        fields = [
            'id',
            'challenge',
            'challenge_title',
            'started_at',
            'deadline_at',
            'last_saved_at',
            'is_submitted',
            'submitted_at',
            'total_score',
            'points_awarded',
            'is_within_time_limit',
            'completion_time_seconds',
            'submission_timing_status',
            'answers',
        ]
        read_only_fields = fields

    def get_completion_time_seconds(self, obj):
        if not obj.started_at or not obj.submitted_at:
            return None
        delta = obj.submitted_at - obj.started_at
        return int(delta.total_seconds())

    def get_submission_timing_status(self, obj):
        if not obj.is_submitted:
            return 'not_submitted'
        return 'on_time' if obj.is_within_time_limit else 'late'


class ChallengeSubmissionResultSerializer(serializers.ModelSerializer):
    challenge_title = serializers.CharField(source='challenge.title', read_only=True)
    answers = ChallengeSubmissionAnswerSerializer(many=True, read_only=True)
    completion_time_seconds = serializers.SerializerMethodField()
    submission_timing_status = serializers.SerializerMethodField()

    class Meta:
        model = ChallengeAttempt
        fields = [
            'id',
            'challenge',
            'challenge_title',
            'started_at',
            'deadline_at',
            'last_saved_at',
            'is_submitted',
            'submitted_at',
            'total_score',
            'points_awarded',
            'is_within_time_limit',
            'completion_time_seconds',
            'submission_timing_status',
            'answers',
        ]
        read_only_fields = fields

    def get_completion_time_seconds(self, obj):
        if not obj.started_at or not obj.submitted_at:
            return None
        delta = obj.submitted_at - obj.started_at
        return int(delta.total_seconds())

    def get_submission_timing_status(self, obj):
        if not obj.is_submitted:
            return 'not_submitted'
        return 'on_time' if obj.is_within_time_limit else 'late'


