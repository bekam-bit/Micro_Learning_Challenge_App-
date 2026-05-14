from django.db import models
from apps.users.models import User


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-id']
        indexes = [
            models.Index(fields=['user', 'is_read', 'created_at'], name='notif_user_read_ct_idx'),
            models.Index(fields=['created_at'], name='notif_created_idx'),
        ]

    def __str__(self):
        return f'Notification #{self.pk} for user {self.user_id}'


class NotificationRetentionSetting(models.Model):
    singleton_key = models.PositiveSmallIntegerField(default=1, unique=True, editable=False)
    enabled = models.BooleanField(default=True)
    retention_days = models.PositiveIntegerField(default=30)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Notification Retention Setting'
        verbose_name_plural = 'Notification Retention Setting'

    def save(self, *args, **kwargs):
        self.singleton_key = 1
        super().save(*args, **kwargs)

    def __str__(self):
        status = 'enabled' if self.enabled else 'disabled'
        return f'Notification retention ({status}, {self.retention_days} days)'