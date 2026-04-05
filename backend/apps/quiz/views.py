from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models.Quiz import Quiz
from .models.Question import Question
from .models.Answer import Answer
from .models.QuizSubmission import QuizSubmission
from .serializers import (
    QuizSerializer,
    QuestionSerializer,
    AnswerSerializer,
    UserQuizSerializer,
    QuizSubmissionSerializer,
)

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
    queryset = Quiz.objects.select_related('lesson__module').prefetch_related('questions', 'questions__answers').all()
    serializer_class = UserQuizSerializer
    permission_classes = [permissions.IsAuthenticated]  # user must be logged in

    def get_queryset(self):
        queryset = super().get_queryset()
        lesson_id = self.request.query_params.get('lesson_id')
        if lesson_id and lesson_id.isdigit():
            queryset = queryset.filter(lesson_id=int(lesson_id))
        return queryset

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
        payload_serializer = QuizSubmissionSerializer(data=request.data)
        payload_serializer.is_valid(raise_exception=True)
        submitted = payload_serializer.validated_data['answers']

        quiz_question_list = list(quiz.questions.all())
        total = len(quiz_question_list)
        correct_count = 0
        quiz_questions = {
            question.id: question
            for question in quiz_question_list
        }
        question_answers_map = {
            question.id: {
                answer.id: answer
                for answer in sorted(question.answers.all(), key=lambda obj: (obj.order, obj.id))
            }
            for question in quiz_question_list
        }
        correct_answers_map = {
            question_id: [
                {
                    'id': answer.id,
                    'text': answer.text,
                    'explanation': answer.explanation,
                }
                for answer in answer_lookup.values()
                if answer.is_correct
            ]
            for question_id, answer_lookup in question_answers_map.items()
        }
        reveal_results = []

        for item in submitted:
            question_id = item.get('question_id')
            question = quiz_questions.get(question_id)

            if question is None:
                return Response(
                    {
                        'detail': f'Question {question_id} does not belong to quiz {quiz.id}.'
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            selected_answers = []
            answer_id = item.get('answer_id')
            answer_ids = item.get('answer_ids') or []

            if question.question_type == Question.TYPE_MULTIPLE_CHOICE:
                if not answer_ids:
                    return Response(
                        {
                            'detail': f'Question {question_id} requires answer_ids for multiple_choice format.'
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                answer_lookup = question_answers_map.get(question_id, {})
                valid_answer_ids = [answer_id_item for answer_id_item in set(answer_ids) if answer_id_item in answer_lookup]
                selected_answers = [
                    answer_lookup[answer_id_item]
                    for answer_id_item in sorted(
                        valid_answer_ids,
                        key=lambda item: (answer_lookup[item].order, answer_lookup[item].id),
                    )
                ]
                if len(selected_answers) != len(set(answer_ids)):
                    return Response(
                        {
                            'detail': f'One or more answer IDs are invalid for question {question_id}.'
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                if answer_id is None:
                    return Response(
                        {
                            'detail': f'Question {question_id} requires answer_id for {question.question_type} format.'
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                answer = question_answers_map.get(question_id, {}).get(answer_id)
                if answer is None:
                    return Response(
                        {
                            'detail': f'Answer {answer_id} is invalid for question {question_id}.'
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                selected_answers = [answer]

            correct_answers = correct_answers_map.get(question_id, [])

            selected_answer_ids = {answer.id for answer in selected_answers}
            correct_answer_ids = {item['id'] for item in correct_answers}

            if question.question_type == Question.TYPE_MULTIPLE_CHOICE:
                is_correct = selected_answer_ids == correct_answer_ids
            else:
                is_correct = selected_answers[0].is_correct

            if is_correct:
                correct_count += 1

            selected_answer = selected_answers[0]
            explanation = selected_answer.explanation.strip() if selected_answer.explanation else ''
            if not explanation:
                if is_correct:
                    explanation = 'Correct choice. Nice work.'
                else:
                    correct_text = ', '.join(item['text'] for item in correct_answers)
                    explanation = f'Incorrect choice. Correct answer: {correct_text}' if correct_text else 'Incorrect choice.'

            reveal_results.append(
                {
                    'question_id': question_id,
                    'question_type': question.question_type,
                    'selected_answer': {
                        'id': selected_answer.id,
                        'text': selected_answer.text,
                        'explanation': selected_answer.explanation,
                    },
                    'selected_answers': [
                        {
                            'id': answer.id,
                            'text': answer.text,
                            'explanation': answer.explanation,
                        }
                        for answer in selected_answers
                    ],
                    'is_correct': is_correct,
                    'correct_answers': correct_answers,
                    'explanation': explanation,
                }
            )

        score = int((correct_count / total) * 100) if total > 0 else 0

        QuizSubmission.objects.update_or_create(
            quiz=quiz,
            user=request.user,
            defaults={
                'is_submitted': True,
                'total_questions': total,
                'correct_answers': correct_count,
                'score': score,
            },
        )

        if quiz.lesson_id and quiz.lesson and quiz.lesson.module_id:
            from apps.progress.models import UserProgress

            UserProgress.sync_module_progress(user=request.user, module=quiz.lesson.module)

        return Response({
            "total_questions": total,
            "correct_answers": correct_count,
            "score": score,
            "results": reveal_results,
        }, status=status.HTTP_200_OK)
