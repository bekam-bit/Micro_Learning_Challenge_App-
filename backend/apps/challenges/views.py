from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
import json

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from config.api_cache import get_cached_response, invalidate_namespace, set_cached_response
from config.pagination import StandardPageNumberPagination

from apps.users.permissions import IsAdminRole, IsLearnerRole
from apps.users.services import register_challenge_completion_activity

from .models import (
    Challenge,
    ChallengeAttempt,
    ChallengeAttemptAnswer,
    ChallengeQuestion,
    ChallengeSubmission,
    ChallengeSubmissionIdempotency,
)
from .serializers import (
	ChallengeAttemptSerializer,
    ChallengeDetailSerializer,
	ChallengeProgressUpsertSerializer,
	ChallengeQuestionAdminSerializer,
	ChallengeQuestionPublicSerializer,
	ChallengeSerializer,
	ChallengeSubmissionResultSerializer,
	ChallengeSubmissionSerializer,
)


class ChallengeListCreateView(generics.ListCreateAPIView):
    queryset = Challenge.objects.select_related('lesson', 'module', 'category').all()
    serializer_class = ChallengeSerializer
    pagination_class = StandardPageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset()

        scope = self.request.query_params.get('scope')
        if scope == 'lesson':
            queryset = queryset.filter(lesson__isnull=False)
        elif scope == 'module':
            queryset = queryset.filter(module__isnull=False)
        elif scope == 'category':
            queryset = queryset.filter(category__isnull=False)

        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)

        lesson_id = self.request.query_params.get('lesson_id')
        if lesson_id:
            queryset = queryset.filter(lesson_id=lesson_id)

        module_id = self.request.query_params.get('module_id')
        if module_id:
            queryset = queryset.filter(module_id=module_id)

        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(title__icontains=search)

        sort_by = self.request.query_params.get('sort_by', '-created_at')
        allowed_sort_fields = {'title', '-title', 'points', '-points', 'difficulty', '-difficulty', 'created_at', '-created_at'}
        if sort_by not in allowed_sort_fields:
            sort_by = '-created_at'

        return queryset.order_by(sort_by, 'id')

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAdminRole()]

    def list(self, request, *args, **kwargs):
        cached_response = get_cached_response(request, namespace='challenges')
        if cached_response is not None:
            return cached_response

        response = super().list(request, *args, **kwargs)
        set_cached_response(request, namespace='challenges', response=response)
        return response

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        if response.status_code < 400:
            invalidate_namespace('challenges')
        return response


class ChallengeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Challenge.objects.select_related('lesson', 'module', 'category').all()

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return ChallengeDetailSerializer
        return ChallengeSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAdminRole()]

    def retrieve(self, request, *args, **kwargs):
        cached_response = get_cached_response(request, namespace='challenges')
        if cached_response is not None:
            return cached_response

        response = super().retrieve(request, *args, **kwargs)
        set_cached_response(request, namespace='challenges', response=response)
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if response.status_code < 400:
            invalidate_namespace('challenges')
        return response

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        if response.status_code < 400:
            invalidate_namespace('challenges')
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        if response.status_code < 400:
            invalidate_namespace('challenges')
        return response


class ChallengeQuestionListCreateView(generics.ListCreateAPIView):
    pagination_class = StandardPageNumberPagination

    def get_queryset(self):
        challenge_id = self.kwargs['challenge_id']
        return ChallengeQuestion.objects.filter(challenge_id=challenge_id).order_by('order', 'id')

    def get_serializer_class(self):
        user = self.request.user
        if self.request.method == 'POST':
            return ChallengeQuestionAdminSerializer
        if user.is_authenticated and user.role == 'admin':
            return ChallengeQuestionAdminSerializer
        return ChallengeQuestionPublicSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAdminRole()]

    def perform_create(self, serializer):
        challenge = get_object_or_404(Challenge, pk=self.kwargs['challenge_id'])
        serializer.save(challenge=challenge)
        invalidate_namespace('challenges')

    def list(self, request, *args, **kwargs):
        cached_response = get_cached_response(request, namespace='challenges')
        if cached_response is not None:
            return cached_response

        response = super().list(request, *args, **kwargs)
        set_cached_response(request, namespace='challenges', response=response)
        return response


class ChallengeQuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ChallengeQuestion.objects.select_related('challenge').all()

    def get_serializer_class(self):
        user = self.request.user
        if self.request.method in {'PUT', 'PATCH', 'DELETE'}:
            return ChallengeQuestionAdminSerializer
        if user.is_authenticated and user.role == 'admin':
            return ChallengeQuestionAdminSerializer
        return ChallengeQuestionPublicSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAdminRole()]

    def retrieve(self, request, *args, **kwargs):
        cached_response = get_cached_response(request, namespace='challenges')
        if cached_response is not None:
            return cached_response

        response = super().retrieve(request, *args, **kwargs)
        set_cached_response(request, namespace='challenges', response=response)
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        if response.status_code < 400:
            invalidate_namespace('challenges')
        return response

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        if response.status_code < 400:
            invalidate_namespace('challenges')
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        if response.status_code < 400:
            invalidate_namespace('challenges')
        return response


def _normalize_answer(value):
    return ' '.join((value or '').strip().lower().split())


def _normalize_multiple_choice(values):
    normalized = sorted({_normalize_answer(value) for value in values if _normalize_answer(value)})
    return normalized


def _canonicalize_answer_text(question, answer_data):
    if question.question_type == ChallengeQuestion.TYPE_MULTIPLE_CHOICE:
        values = answer_data.get('answer_options', [])
        if not values and answer_data.get('answer_text'):
            values = [part.strip() for part in answer_data['answer_text'].split(',')]
        return json.dumps(_normalize_multiple_choice(values))

    if question.question_type == ChallengeQuestion.TYPE_NUMERIC:
        if answer_data.get('answer_number') is not None:
            return str(answer_data['answer_number'])
        return str(answer_data.get('answer_text', ''))

    if question.question_type == ChallengeQuestion.TYPE_TRUE_FALSE:
        if answer_data.get('answer_boolean') is not None:
            return 'true' if answer_data['answer_boolean'] else 'false'
        return _normalize_answer(answer_data.get('answer_text', ''))

    return answer_data.get('answer_text', '')


def _is_answer_correct(question, answer_text):
    if question.question_type == ChallengeQuestion.TYPE_MULTIPLE_CHOICE:
        try:
            submitted_values = json.loads(answer_text or '[]')
        except json.JSONDecodeError:
            submitted_values = []
        expected_values = _normalize_multiple_choice(question.correct_options)
        return _normalize_multiple_choice(submitted_values) == expected_values

    if question.question_type == ChallengeQuestion.TYPE_NUMERIC:
        try:
            submitted_number = float(answer_text)
            expected_number = float(question.correct_answer)
        except (TypeError, ValueError):
            return False
        return abs(submitted_number - expected_number) <= question.numeric_tolerance

    if question.question_type == ChallengeQuestion.TYPE_TRUE_FALSE:
        return _normalize_answer(answer_text) == _normalize_answer(question.correct_answer)

    if question.question_type == ChallengeQuestion.TYPE_SINGLE_CHOICE:
        return _normalize_answer(answer_text) == _normalize_answer(question.correct_answer)

    return _normalize_answer(answer_text) == _normalize_answer(question.correct_answer)


def _upsert_attempt_answers(attempt, answers_payload):
    question_map = {
        question.id: question
        for question in attempt.challenge.questions.all()
    }

    canonical_answers_by_question_id = {}

    for answer_data in answers_payload:
        question_id = answer_data['question_id']
        question = question_map.get(question_id)
        if question is None:
            raise ValueError(f'Question {question_id} does not belong to challenge {attempt.challenge_id}.')

        canonical_answers_by_question_id[question_id] = _canonicalize_answer_text(question, answer_data)

    if not canonical_answers_by_question_id:
        return

    existing_answers = {
        answer.question_id: answer
        for answer in attempt.answers.filter(question_id__in=canonical_answers_by_question_id.keys())
    }

    answers_to_create = []
    answers_to_update = []

    for question_id, canonical_answer in canonical_answers_by_question_id.items():
        existing = existing_answers.get(question_id)
        if existing is None:
            answers_to_create.append(
                ChallengeAttemptAnswer(
                    attempt=attempt,
                    question_id=question_id,
                    answer_text=canonical_answer,
                )
            )
            continue

        if existing.answer_text != canonical_answer:
            existing.answer_text = canonical_answer
            answers_to_update.append(existing)

    if answers_to_create:
        ChallengeAttemptAnswer.objects.bulk_create(answers_to_create)

    if answers_to_update:
        ChallengeAttemptAnswer.objects.bulk_update(answers_to_update, ['answer_text'])


def _grade_attempt(attempt):
    all_questions = list(attempt.challenge.questions.all())
    answers = list(attempt.answers.select_related('question').all())
    answer_by_question_id = {answer.question_id: answer for answer in answers}

    missing_answers = [
        ChallengeAttemptAnswer(attempt=attempt, question=question, answer_text='')
        for question in all_questions
        if question.id not in answer_by_question_id
    ]
    if missing_answers:
        created_answers = ChallengeAttemptAnswer.objects.bulk_create(missing_answers)
        for answer in created_answers:
            answer_by_question_id[answer.question_id] = answer

    total_score = 0
    max_score = 0
    answers_to_update = []

    for question in all_questions:
        max_score += question.max_score
        answer = answer_by_question_id[question.id]

        is_correct = _is_answer_correct(question, answer.answer_text)
        score = question.max_score if is_correct else 0
        if answer.is_correct != is_correct or answer.score != score:
            answer.is_correct = is_correct
            answer.score = score
            answers_to_update.append(answer)
        total_score += score

    if answers_to_update:
        ChallengeAttemptAnswer.objects.bulk_update(answers_to_update, ['is_correct', 'score'])

    within_time_limit = not attempt.has_expired()
    if within_time_limit and max_score > 0:
        points_awarded = round((attempt.challenge.points * total_score) / max_score)
    else:
        points_awarded = 0

    attempt.total_score = total_score
    attempt.points_awarded = points_awarded
    attempt.is_within_time_limit = within_time_limit
    attempt.is_submitted = True
    attempt.submitted_at = timezone.now()
    attempt.save(
        update_fields=[
            'total_score',
            'points_awarded',
            'is_within_time_limit',
            'is_submitted',
            'submitted_at',
            'last_saved_at',
        ]
    )
    attempt.update_user_progress()
    register_challenge_completion_activity(attempt.user, points_earned=attempt.points_awarded)
    return max_score


def _build_submission_response(submission, attempt, replayed=False, *, max_score=None):
    if max_score is None:
        max_score = attempt.challenge.questions.aggregate(total=Sum('max_score'))['total'] or 0
    response_data = ChallengeSubmissionSerializer(submission).data
    response_data['max_score'] = max_score
    response_data['within_time_limit'] = attempt.is_within_time_limit
    response_data['deadline_at'] = attempt.deadline_at
    response_data['submitted_at'] = attempt.submitted_at
    response_data['submission_timing_status'] = 'on_time' if attempt.is_within_time_limit else 'late'
    if attempt.started_at and attempt.submitted_at:
        response_data['completion_time_seconds'] = int((attempt.submitted_at - attempt.started_at).total_seconds())
    else:
        response_data['completion_time_seconds'] = None
    response_data['points_awarded'] = attempt.points_awarded
    response_data['idempotency_replayed'] = replayed
    if hasattr(attempt, '_prefetched_objects_cache') and 'answers' in attempt._prefetched_objects_cache:
        result_attempt = attempt
    else:
        result_attempt = ChallengeAttempt.objects.prefetch_related('answers', 'answers__question').get(pk=attempt.pk)

    response_data['results'] = ChallengeSubmissionResultSerializer(result_attempt).data
    return response_data


class ChallengeProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsLearnerRole]

    def get(self, request, challenge_id):
        challenge = get_object_or_404(Challenge, pk=challenge_id)
        attempt = ChallengeAttempt.objects.filter(challenge=challenge, user=request.user).prefetch_related(
            'answers', 'answers__question'
        ).first()

        if attempt is None:
            return Response({'detail': 'No attempt yet.'}, status=status.HTTP_404_NOT_FOUND)

        data = ChallengeAttemptSerializer(attempt).data
        return Response(data, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request, challenge_id):
        challenge = get_object_or_404(Challenge, pk=challenge_id)
        serializer = ChallengeProgressUpsertSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        attempt, _ = ChallengeAttempt.objects.select_for_update().get_or_create(
            challenge=challenge,
            user=request.user,
        )

        if attempt.is_submitted:
            return Response(
                {'detail': 'Challenge is already submitted and cannot be edited.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if attempt.has_expired():
            return Response(
                {'detail': 'Time limit exceeded. Latest saved progress is preserved, but updates are closed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            _upsert_attempt_answers(attempt, serializer.validated_data['answers'])
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        attempt.update_user_progress()
        attempt = ChallengeAttempt.objects.prefetch_related('answers', 'answers__question').get(pk=attempt.pk)
        data = ChallengeAttemptSerializer(attempt).data
        return Response(data, status=status.HTTP_200_OK)


class ChallengeSubmitView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsLearnerRole]

    @transaction.atomic
    def post(self, request, challenge_id):
        challenge = get_object_or_404(Challenge, pk=challenge_id)
        payload_serializer = ChallengeProgressUpsertSerializer(data=request.data)
        payload_serializer.is_valid(raise_exception=True)
        idempotency_key = request.headers.get('X-Idempotency-Key')
        idempotency_record = None

        if idempotency_key and len(idempotency_key) > 128:
            return Response({'detail': 'X-Idempotency-Key must be 128 characters or fewer.'}, status=status.HTTP_400_BAD_REQUEST)

        attempt, _ = ChallengeAttempt.objects.select_for_update().get_or_create(
            challenge=challenge,
            user=request.user,
        )

        if idempotency_key:
            idempotency_record, _ = ChallengeSubmissionIdempotency.objects.select_for_update().get_or_create(
                challenge=challenge,
                user=request.user,
                key=idempotency_key,
            )
            if idempotency_record.submission_id:
                replay_submission = idempotency_record.submission
                replay_attempt = replay_submission.attempt
                if replay_attempt is not None:
                    return Response(
                        _build_submission_response(replay_submission, replay_attempt, replayed=True),
                        status=status.HTTP_200_OK,
                    )

        if attempt.is_submitted:
            return Response({'detail': 'Challenge is already submitted.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            _upsert_attempt_answers(attempt, payload_serializer.validated_data['answers'])
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        max_score = _grade_attempt(attempt)
        submission, _ = ChallengeSubmission.objects.update_or_create(
            attempt=attempt,
            defaults={
                'challenge': challenge,
                'user': request.user,
                'response_text': f'Submitted {attempt.answers.count()} answers.',
                'status': ChallengeSubmission.STATUS_REVIEWED,
                'score': attempt.total_score,
            },
        )

        if idempotency_record is not None:
            idempotency_record.submission = submission
            idempotency_record.save(update_fields=['submission', 'updated_at'])

        hydrated_attempt = ChallengeAttempt.objects.prefetch_related('answers', 'answers__question').get(pk=attempt.pk)
        response_data = _build_submission_response(
            submission,
            hydrated_attempt,
            replayed=False,
            max_score=max_score,
        )
        return Response(response_data, status=status.HTTP_201_CREATED)


class MyChallengeSubmissionsView(generics.ListAPIView):
    serializer_class = ChallengeSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated, IsLearnerRole]
    pagination_class = StandardPageNumberPagination

    def get_queryset(self):
        queryset = ChallengeSubmission.objects.select_related('challenge', 'user', 'attempt').filter(user=self.request.user)

        challenge_id = self.request.query_params.get('challenge_id')
        if challenge_id:
            queryset = queryset.filter(challenge_id=challenge_id)

        return queryset
