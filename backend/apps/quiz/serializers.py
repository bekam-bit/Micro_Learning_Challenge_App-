from rest_framework import serializers
from .models.Quiz import Quiz
from .models.Question import Question
from .models.Answer import Answer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'text', 'explanation', 'is_correct', 'order']


class UserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'text', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'quiz', 'prompt', 'question_type', 'order', 'answers']


class UserQuestionSerializer(serializers.ModelSerializer):
    answers = UserAnswerSerializer(many=True, read_only=True)
    answer_format = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'prompt', 'question_type', 'order', 'answers', 'answer_format']

    def get_answer_format(self, obj):
        if obj.question_type == Question.TYPE_MULTIPLE_CHOICE:
            return {
                'field': 'answer_ids',
                'type': 'integer[]',
                'description': 'Submit one or more answer IDs.',
            }
        return {
            'field': 'answer_id',
            'type': 'integer',
            'description': 'Submit exactly one answer ID.',
        }


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'lesson', 'title', 'description', 'created_at', 'updated_at', 'questions']


class UserQuizSerializer(serializers.ModelSerializer):
    questions = UserQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'lesson', 'title', 'description', 'created_at', 'updated_at', 'questions']


class QuizSubmissionAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer_id = serializers.IntegerField(required=False)
    answer_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        allow_empty=False,
    )


class QuizSubmissionSerializer(serializers.Serializer):
    answers = QuizSubmissionAnswerSerializer(many=True)