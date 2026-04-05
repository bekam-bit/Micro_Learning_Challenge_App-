from django.conf import settings
from django.db import models


class QuizSubmission(models.Model):
    quiz = models.ForeignKey("quiz.Quiz", on_delete=models.CASCADE, related_name="submissions")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="quiz_submissions")
    is_submitted = models.BooleanField(default=True)
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    score = models.PositiveIntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["quiz", "user"], name="unique_quiz_submission_per_user"),
        ]
        indexes = [
            models.Index(fields=["user", "is_submitted"], name="quizsub_user_submitted_idx"),
            models.Index(fields=["quiz", "is_submitted"], name="quizsub_quiz_submitted_idx"),
            models.Index(fields=["submitted_at"], name="quizsub_submitted_at_idx"),
        ]
        ordering = ["-submitted_at", "-id"]

    def __str__(self):
        return f"{self.user} - {self.quiz} ({self.score}%)"
