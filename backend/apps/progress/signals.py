from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.users.models import UserProfile

from .models import UserProgress


def _sync_user_profile_from_progress(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)

    challenge_progress = UserProgress.objects.filter(user=user, challenge__isnull=False)
    lesson_progress = UserProgress.objects.filter(user=user, lesson__isnull=False)
    module_progress = UserProgress.objects.filter(user=user, module__isnull=False)

    profile.challenges_total_count = challenge_progress.count()
    profile.challenges_completed_count = challenge_progress.filter(completed=True).count()
    profile.lessons_total_count = lesson_progress.count()
    profile.lessons_completed_count = lesson_progress.filter(completed=True).count()
    profile.modules_total_count = module_progress.count()
    profile.modules_completed_count = module_progress.filter(completed=True).count()
    profile.save(
        update_fields=[
            "challenges_total_count",
            "challenges_completed_count",
            "lessons_total_count",
            "lessons_completed_count",
            "modules_total_count",
            "modules_completed_count",
        ]
    )


@receiver(post_save, sender=UserProgress)
def sync_profile_after_progress_save(sender, instance, **kwargs):
    _sync_user_profile_from_progress(instance.user)


@receiver(post_delete, sender=UserProgress)
def sync_profile_after_progress_delete(sender, instance, **kwargs):
    _sync_user_profile_from_progress(instance.user)
