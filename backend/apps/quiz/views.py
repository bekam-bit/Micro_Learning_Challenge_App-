from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models.Quiz import Quiz
from .models.Question import Question
from .models.Answer import Answer
from .serializers import QuizSerializer, QuestionSerializer, AnswerSerializer

# -------------------
# Admin ViewSets
# -------------------
class QuizAdminViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAdminUser]


class QuestionAdminViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAdminUser]


class AnswerAdminViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAdminUser]


# -------------------
# User Quiz View
# -------------------
class QuizUserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    User can view quizzes with questions and answers.
    Submission of answers handled via custom action.
    """
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]  # user must be logged in

    @action(detail=True, methods=['POST'], url_path='submit')
    def submit_quiz(self, request, pk=None):
        """
        Expects:
        {
            "answers": [
                {"question_id": 1, "answer_id": 5},
                {"question_id": 2, "answer_id": 9}
            ]
        }
        Returns:
        {
            "total_questions": 2,
            "correct_answers": 2,
            "score": 100
        }
        """
        quiz = self.get_object()
        submitted = request.data.get('answers', [])

        total = quiz.questions.count()
        correct_count = 0

        for item in submitted:
            question_id = item.get('question_id')
            answer_id = item.get('answer_id')
            try:
                answer = Answer.objects.get(id=answer_id, question_id=question_id)
                if answer.is_correct:
                    correct_count += 1
            except Answer.DoesNotExist:
                continue  # skip invalid answers

        score = int((correct_count / total) * 100) if total > 0 else 0

        return Response({
            "total_questions": total,
            "correct_answers": correct_count,
            "score": score
        }, status=status.HTTP_200_OK)
