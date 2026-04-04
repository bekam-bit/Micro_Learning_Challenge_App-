from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.categories.models import Category
from apps.lessons.models import Lesson
from apps.modules.models import Module

class Challenge(models.Model):
    DIFFICULTY_CHOICES = (
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES)
    points = models.PositiveIntegerField(default=10)
    time_limit_minutes = models.PositiveIntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='challenges',
        null=True,
        blank=True,
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='challenges',
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='challenges',
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(lesson__isnull=False, module__isnull=True, category__isnull=True)
                    | Q(lesson__isnull=True, module__isnull=False, category__isnull=True)
                    | Q(lesson__isnull=True, module__isnull=True, category__isnull=False)
                ),
                name='challenge_exactly_one_owner',
            )
        ]

    def get_scope(self):
        if self.lesson_id:
            return 'lesson'
        if self.module_id:
            return 'module'
        return 'category'

    def get_scope_display(self):
        return self.get_scope().title()

    def __str__(self):
        return self.title


class ChallengeQuestion(models.Model):
    TYPE_SINGLE_CHOICE = 'single_choice'
    TYPE_MULTIPLE_CHOICE = 'multiple_choice'
    TYPE_TRUE_FALSE = 'true_false'
    TYPE_NUMERIC = 'numeric'
    TYPE_SHORT_TEXT_STRICT = 'short_text_strict'

    QUESTION_TYPE_CHOICES = (
        (TYPE_SINGLE_CHOICE, 'Single Choice'),
        (TYPE_MULTIPLE_CHOICE, 'Multiple Choice'),
        (TYPE_TRUE_FALSE, 'True / False'),
        (TYPE_NUMERIC, 'Numeric'),
        (TYPE_SHORT_TEXT_STRICT, 'Short Text (Strict)'),
    )

    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=30, choices=QUESTION_TYPE_CHOICES, default=TYPE_SHORT_TEXT_STRICT)
    options = models.JSONField(default=list, blank=True)
    correct_options = models.JSONField(default=list, blank=True)
    correct_answer = models.TextField()
    numeric_tolerance = models.FloatField(default=0)
    explanation = models.TextField(blank=True, default='')
    max_score = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def clean(self):
        options = self.options or []
        correct_options = self.correct_options or []
        correct_answer = (self.correct_answer or '').strip()
        errors = {}

        if self.question_type in {self.TYPE_SINGLE_CHOICE, self.TYPE_MULTIPLE_CHOICE} and not options:
            errors['options'] = 'Options are required for choice question types.'

        if self.question_type == self.TYPE_SINGLE_CHOICE:
            if not correct_answer:
                errors['correct_answer'] = 'Single choice requires a correct answer.'
            elif correct_answer not in options:
                errors['correct_answer'] = 'Correct answer must be one of the available options.'

        if self.question_type == self.TYPE_MULTIPLE_CHOICE:
            if not correct_options:
                errors['correct_options'] = 'Multiple choice requires at least one correct option.'
            else:
                invalid = [value for value in correct_options if value not in options]
                if invalid:
                    errors['correct_options'] = 'Each correct option must exist in options.'

        if self.question_type == self.TYPE_TRUE_FALSE:
            if correct_answer.lower() not in {'true', 'false'}:
                errors['correct_answer'] = 'True/False requires correct_answer to be true or false.'

        if self.question_type == self.TYPE_NUMERIC:
            try:
                float(correct_answer)
            except (TypeError, ValueError):
                errors['correct_answer'] = 'Numeric questions require a numeric correct answer.'
            if self.numeric_tolerance < 0:
                errors['numeric_tolerance'] = 'Numeric tolerance must be greater than or equal to zero.'

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f'{self.challenge.title} - Q{self.order}'


class ChallengeAttempt(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='attempts')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='challenge_attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    deadline_at = models.DateTimeField(blank=True, null=True)
    last_saved_at = models.DateTimeField(auto_now=True)
    is_submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(blank=True, null=True)
    total_score = models.PositiveIntegerField(default=0)
    points_awarded = models.PositiveIntegerField(default=0)
    is_within_time_limit = models.BooleanField(default=True)

    class Meta:
        unique_together = ('challenge', 'user')

    def initialize_deadline(self):
        if self.deadline_at is None and self.challenge_id:
            self.deadline_at = timezone.now() + timedelta(minutes=self.challenge.time_limit_minutes)

    def has_expired(self):
        if not self.deadline_at:
            return False
        return timezone.now() > self.deadline_at

    def save(self, *args, **kwargs):
        if self.deadline_at is None and self.challenge_id:
            self.initialize_deadline()
        super().save(*args, **kwargs)

    def update_user_progress(self):
        from apps.points.models import PointTransaction
        from apps.points.services import upsert_point_transaction
        from apps.progress.models import UserProgress

        question_count = self.challenge.questions.count()
        answered_count = self.answers.exclude(answer_text='').count()
        UserProgress.upsert_challenge_progress(
            user=self.user,
            challenge=self.challenge,
            completed=self.is_submitted,
            points_earned=self.points_awarded,
            completed_parts=answered_count,
            total_parts=question_count,
        )

        if self.is_submitted:
            upsert_point_transaction(
                user=self.user,
                points=self.points_awarded,
                source_type=PointTransaction.SOURCE_CHALLENGE_ATTEMPT,
                source_id=self.id,
                reason='Challenge submission reward',
                metadata={
                    'challenge_id': self.challenge_id,
                    'attempt_id': self.id,
                },
            )

        if self.challenge.lesson_id:
            UserProgress.sync_lesson_progress(user=self.user, lesson=self.challenge.lesson)
            if self.challenge.lesson.module_id:
                UserProgress.sync_module_progress(user=self.user, module=self.challenge.lesson.module)
        elif self.challenge.module_id:
            UserProgress.sync_module_progress(user=self.user, module=self.challenge.module)


class ChallengeAttemptAnswer(models.Model):
    attempt = models.ForeignKey(ChallengeAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(ChallengeQuestion, on_delete=models.CASCADE, related_name='attempt_answers')
    answer_text = models.TextField(blank=True, default='')
    is_correct = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('attempt', 'question')
        ordering = ['question__order', 'question_id']

    def __str__(self):
        return f'Attempt {self.attempt_id} - Question {self.question_id}'


class ChallengeSubmission(models.Model):
    STATUS_SUBMITTED = 'submitted'
    STATUS_REVIEWED = 'reviewed'

    STATUS_CHOICES = (
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_REVIEWED, 'Reviewed'),
    )

    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='submissions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='challenge_submissions')
    attempt = models.OneToOneField(ChallengeAttempt, on_delete=models.CASCADE, related_name='submission', null=True, blank=True)
    response_text = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUBMITTED)
    score = models.PositiveIntegerField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.user} - {self.challenge.title}'


class ChallengeSubmissionIdempotency(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='idempotency_keys')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='challenge_submission_idempotency_keys')
    key = models.CharField(max_length=128)
    submission = models.OneToOneField(ChallengeSubmission, on_delete=models.CASCADE, related_name='idempotency_record', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('challenge', 'user', 'key')

    def __str__(self):
        return f'{self.user} - {self.challenge} - {self.key}'
