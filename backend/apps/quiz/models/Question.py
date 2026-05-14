from django.db import models


class Question(models.Model):
    TYPE_SINGLE_CHOICE = 'single_choice'
    TYPE_MULTIPLE_CHOICE = 'multiple_choice'
    TYPE_TRUE_FALSE = 'true_false'

    QUESTION_TYPE_CHOICES = (
        (TYPE_SINGLE_CHOICE, 'Single Choice'),
        (TYPE_MULTIPLE_CHOICE, 'Multiple Choice'),
        (TYPE_TRUE_FALSE, 'True / False'),
    )

    quiz = models.ForeignKey("quiz.Quiz", on_delete=models.CASCADE, related_name="questions")
    prompt = models.TextField()
    question_type = models.CharField(max_length=30, choices=QUESTION_TYPE_CHOICES, default=TYPE_SINGLE_CHOICE)
    order = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Q{self.order}: {self.prompt[:60]}"