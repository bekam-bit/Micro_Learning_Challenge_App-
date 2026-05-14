from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Notification, NotificationRetentionSetting


User = get_user_model()


def get_retention_setting():
    setting, _ = NotificationRetentionSetting.objects.get_or_create(singleton_key=1)
    return setting


def cleanup_old_read_notifications():
    setting = get_retention_setting()

    if not setting.enabled:
        return 0

    cutoff = timezone.now() - timedelta(days=setting.retention_days)
    deleted_count, _ = Notification.objects.filter(is_read=True, created_at__lt=cutoff).delete()
    return deleted_count


def create_notification(*, user, message):
    notification = Notification.objects.create(user=user, message=message)
    cleanup_old_read_notifications()
    return notification


def notify_all_learners(*, message):
    learner_ids = User.objects.filter(role=User.ROLE_LEARNER, is_active=True).values_list('id', flat=True)

    batch_size = 1000
    notifications_batch = []
    total_created = 0

    for user_id in learner_ids.iterator(chunk_size=batch_size):
        notifications_batch.append(Notification(user_id=user_id, message=message))
        if len(notifications_batch) >= batch_size:
            Notification.objects.bulk_create(notifications_batch, batch_size=batch_size)
            total_created += len(notifications_batch)
            notifications_batch.clear()

    if notifications_batch:
        Notification.objects.bulk_create(notifications_batch, batch_size=batch_size)
        total_created += len(notifications_batch)

    if total_created == 0:
        return 0

    cleanup_old_read_notifications()
    return total_created
