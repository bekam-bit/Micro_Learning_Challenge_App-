from django.conf import settings
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    bio = models.TextField(blank=True)
    profile_picture = models.URLField(blank=True)
    total_points = models.PositiveIntegerField(default=0)
    modules_completed_count = models.PositiveIntegerField(default=0)
    modules_total_count = models.PositiveIntegerField(default=0)
    lessons_completed_count = models.PositiveIntegerField(default=0)
    lessons_total_count = models.PositiveIntegerField(default=0)
    challenges_completed_count = models.PositiveIntegerField(default=0)
    challenges_total_count = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)

    @staticmethod
    def _completion_percentage(completed: int, total: int) -> float:
        if total <= 0:
            return 0.0
        return round((completed / total) * 100, 2)

    @property
    def modules_completion_percentage(self) -> float:
        return self._completion_percentage(self.modules_completed_count, self.modules_total_count)

    @property
    def lessons_completion_percentage(self) -> float:
        return self._completion_percentage(self.lessons_completed_count, self.lessons_total_count)

    @property
    def challenges_completion_percentage(self) -> float:
        return self._completion_percentage(self.challenges_completed_count, self.challenges_total_count)

    def __str__(self) -> str:
        return f"{self.user.username} profile"
