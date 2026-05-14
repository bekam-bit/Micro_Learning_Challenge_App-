from rest_framework import serializers

from apps.challenges.models import ChallengeAttempt
from apps.challenges.serializers import ChallengeQuestionPublicSerializer

from .models import Lesson

class LessonSerializer(serializers.ModelSerializer):
    knowledge_check = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'content', 'video_url', 'video_file', 'order',
            'category', 'module', 'created_at', 'updated_at', 'knowledge_check'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        # Ensure at least one of video_url or video_file is provided
        video_url = data.get('video_url')
        video_file = data.get('video_file')
        if not video_url and not video_file:
            raise serializers.ValidationError("Either video_url or video_file must be provided.")
        return data

    def get_knowledge_check(self, obj):
        include_knowledge_check = self.context.get('include_knowledge_check', False)
        if not include_knowledge_check:
            return None

        challenge = obj.challenges.prefetch_related('questions').order_by('created_at', 'id').first()
        if challenge is None:
            return None

        question = challenge.questions.order_by('order', 'id').first()
        question_payload = None
        if question is not None:
            question_payload = ChallengeQuestionPublicSerializer(question, context=self.context).data

        request = self.context.get('request')
        user = getattr(request, 'user', None)
        attempt_payload = None
        if user is not None and user.is_authenticated:
            attempt = ChallengeAttempt.objects.filter(challenge=challenge, user=user).first()
            if attempt is not None:
                attempt_payload = {
                    'attempt_id': attempt.id,
                    'is_submitted': attempt.is_submitted,
                    'started_at': attempt.started_at,
                    'last_saved_at': attempt.last_saved_at,
                    'submitted_at': attempt.submitted_at,
                    'total_score': attempt.total_score,
                    'points_awarded': attempt.points_awarded,
                }

        return {
            'challenge_id': challenge.id,
            'title': challenge.title,
            'description': challenge.description,
            'difficulty': challenge.difficulty,
            'points': challenge.points,
            'time_limit_minutes': challenge.time_limit_minutes,
            'question': question_payload,
            'attempt': attempt_payload,
        }
