from django.db import models


class Answer(models.Model):
    question = models.ForeignKey("quiz.Question", on_delete=models.CASCADE, related_name="answers")
    text = models.CharField(max_length=500)
    explanation = models.TextField(blank=True, default='')
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.text