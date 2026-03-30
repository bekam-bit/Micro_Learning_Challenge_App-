from django.db import models
from apps.lessons.models import Lesson

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
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='challenges')

    def __str__(self):
        return self.title