from django.conf import settings
from django.db import models


class PointTransaction(models.Model):
    SOURCE_CHALLENGE_ATTEMPT = 'challenge_attempt'

    SOURCE_CHOICES = (
        (SOURCE_CHALLENGE_ATTEMPT, 'Challenge Attempt'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='point_transactions',
    )
    points = models.PositiveIntegerField(default=0)
    source_type = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    source_id = models.PositiveBigIntegerField()
    reason = models.CharField(max_length=120, blank=True, default='')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'source_type', 'source_id'],
                name='unique_user_point_source',
            )
        ]
        ordering = ['-created_at', '-id']

    def __str__(self):
        return f'{self.user} {self.points} ({self.source_type}:{self.source_id})'
