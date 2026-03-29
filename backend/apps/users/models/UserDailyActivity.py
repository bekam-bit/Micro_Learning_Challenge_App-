from django.conf import settings
from django.db import models


class UserDailyActivity(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="daily_activities",
    )
    activity_date = models.DateField()
    points_earned = models.PositiveIntegerField(default=0)
    modules_completed = models.PositiveIntegerField(default=0)
    lessons_completed = models.PositiveIntegerField(default=0)
    challenges_completed = models.PositiveIntegerField(default=0)
    activity_score = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "activity_date"],
                name="unique_user_activity_date",
            )
        ]
        ordering = ["activity_date"]

    @staticmethod
    def score_to_level(score: int) -> int:
        if score <= 0:
            return 0
        if score < 20:
            return 1
        if score < 50:
            return 2
        if score < 100:
            return 3
        return 4

    def __str__(self) -> str:
        return f"{self.user.username} - {self.activity_date}"
