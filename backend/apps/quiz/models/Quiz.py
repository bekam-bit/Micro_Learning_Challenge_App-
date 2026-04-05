from django.db import models


class Quiz(models.Model):
    lesson = models.ForeignKey(
        "lessons.Lesson",
        on_delete=models.CASCADE,
        related_name="quizzes",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title