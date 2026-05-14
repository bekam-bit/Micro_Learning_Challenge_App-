from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import PointTransaction
from .services import sync_user_total_points


@receiver(post_save, sender=PointTransaction)
def sync_profile_after_points_save(sender, instance, **kwargs):
    sync_user_total_points(instance.user)


@receiver(post_delete, sender=PointTransaction)
def sync_profile_after_points_delete(sender, instance, **kwargs):
    sync_user_total_points(instance.user)
