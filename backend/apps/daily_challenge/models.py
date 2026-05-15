from django.db import models
from apps.challenges.models import Challenge


class DailyChallenge(models.Model):
    # Use a OneToOneField instead of inheritance to separate ID spaces
    challenge = models.OneToOneField(
        'challenge.Challenge', 
        on_delete=models.CASCADE, 
        related_name='daily_profile'
    )
    date = models.DateField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Daily Challenge: {self.challenge.title}"

    # Proxy properties to maintain compatibility with existing code
    @property
    def title(self):
        return self.challenge.title

    @property
    def description(self):
        return self.challenge.description

    @property
    def lesson(self):
        return self.challenge.lesson

    @property
    def module(self):
        return self.challenge.module

    @property
    def category(self):
        return self.challenge.category

    @property
    def difficulty(self):
        return self.challenge.difficulty

    @property
    def is_daily(self):
        return True