from django.db import models
from django.db.models import Q
from apps.users.models import User
from apps.challenges.models import Challenge
from apps.lessons.models import Lesson
from apps.modules.models import Module

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    challenge = models.ForeignKey(
        Challenge,
        on_delete=models.CASCADE,
        related_name='user_progress',
        null=True,
        blank=True,
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='user_progress',
        null=True,
        blank=True,
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='user_progress',
        null=True,
        blank=True,
    )
    completed = models.BooleanField(default=False)
    points_earned = models.PositiveIntegerField(default=0)
    completed_parts = models.PositiveIntegerField(default=0)
    total_parts = models.PositiveIntegerField(default=0)
    progress_percent = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(challenge__isnull=False, lesson__isnull=True, module__isnull=True)
                    | Q(challenge__isnull=True, lesson__isnull=False, module__isnull=True)
                    | Q(challenge__isnull=True, lesson__isnull=True, module__isnull=False)
                ),
                name='progress_exactly_one_owner',
            ),
            models.UniqueConstraint(
                fields=['user', 'challenge'],
                condition=Q(challenge__isnull=False),
                name='unique_user_challenge_progress',
            ),
            models.UniqueConstraint(
                fields=['user', 'lesson'],
                condition=Q(lesson__isnull=False),
                name='unique_user_lesson_progress',
            ),
            models.UniqueConstraint(
                fields=['user', 'module'],
                condition=Q(module__isnull=False),
                name='unique_user_module_progress',
            ),
        ]

    @staticmethod
    def _calculate_percent(completed_parts: int, total_parts: int) -> int:
        if total_parts <= 0:
            return 0
        percent = int((completed_parts / total_parts) * 100)
        return max(0, min(100, percent))

    @classmethod
    def upsert_challenge_progress(
        cls,
        *,
        user,
        challenge,
        completed: bool,
        points_earned: int,
        completed_parts: int,
        total_parts: int,
    ):
        completed_parts = min(completed_parts, total_parts) if total_parts > 0 else 0
        progress_percent = cls._calculate_percent(completed_parts, total_parts)
        return cls.objects.update_or_create(
            user=user,
            challenge=challenge,
            defaults={
                'lesson': None,
                'module': None,
                'completed': completed,
                'points_earned': points_earned,
                'completed_parts': completed_parts,
                'total_parts': total_parts,
                'progress_percent': progress_percent,
            },
        )

    @classmethod
    def sync_lesson_progress(cls, *, user, lesson):
        total_parts = lesson.challenges.count()
        completed_parts = cls.objects.filter(
            user=user,
            challenge__lesson=lesson,
            challenge__isnull=False,
            completed=True,
        ).count()
        completed_parts = min(completed_parts, total_parts) if total_parts > 0 else 0
        progress_percent = cls._calculate_percent(completed_parts, total_parts)
        completed = total_parts > 0 and completed_parts >= total_parts

        return cls.objects.update_or_create(
            user=user,
            lesson=lesson,
            defaults={
                'challenge': None,
                'module': None,
                'completed': completed,
                'points_earned': 0,
                'completed_parts': completed_parts,
                'total_parts': total_parts,
                'progress_percent': progress_percent,
            },
        )

    @classmethod
    def sync_module_progress(cls, *, user, module):
        total_lessons = module.lessons.count()
        completed_lessons = cls.objects.filter(
            user=user,
            lesson__module=module,
            lesson__isnull=False,
            completed=True,
        ).count()

        direct_module_challenges_total = module.challenges.filter(lesson__isnull=True).count()
        direct_module_challenges_completed = cls.objects.filter(
            user=user,
            challenge__module=module,
            challenge__lesson__isnull=True,
            challenge__isnull=False,
            completed=True,
        ).count()

        total_parts = total_lessons + direct_module_challenges_total
        completed_parts = completed_lessons + direct_module_challenges_completed
        completed_parts = min(completed_parts, total_parts) if total_parts > 0 else 0
        progress_percent = cls._calculate_percent(completed_parts, total_parts)
        completed = total_parts > 0 and completed_parts >= total_parts

        return cls.objects.update_or_create(
            user=user,
            module=module,
            defaults={
                'challenge': None,
                'lesson': None,
                'completed': completed,
                'points_earned': 0,
                'completed_parts': completed_parts,
                'total_parts': total_parts,
                'progress_percent': progress_percent,
            },
        )

    def save(self, *args, **kwargs):
        if self.total_parts > 0:
            self.completed_parts = min(self.completed_parts, self.total_parts)
            self.progress_percent = self._calculate_percent(self.completed_parts, self.total_parts)
        else:
            self.completed_parts = 0
            self.progress_percent = 0
        super().save(*args, **kwargs)

    def __str__(self):
        if self.challenge_id:
            target = self.challenge.title
        elif self.lesson_id:
            target = self.lesson.title
        else:
            target = self.module.title
        return f"{self.user.username} - {target}"