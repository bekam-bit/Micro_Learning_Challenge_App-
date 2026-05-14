from django.db import models
from apps.challenges.models import Challenge


class DailyChallenge(Challenge):
    date = models.DateField(unique=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.date} - {self.title}"