from django.db import models
from challenges.models import Challenge

class DailyChallenge(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='daily_entries')
    date = models.DateField(unique=True)

    def __str__(self):
        return f"{self.date} - {self.challenge.title}"