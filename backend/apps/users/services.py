from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import UserDailyActivity, UserProfile


def _compute_daily_activity_score(*, activity):
    # Keep scoring simple and extensible for future activity sources.
    return (
        activity.points_earned
        + (activity.challenges_completed * 10)
        + (activity.lessons_completed * 5)
        + (activity.modules_completed * 20)
    )


@transaction.atomic
def _register_learning_activity(
    user,
    *,
    points_earned=0,
    challenges_completed=0,
    lessons_completed=0,
    modules_completed=0,
):
    today = timezone.localdate()

    profile, _ = UserProfile.objects.select_for_update().get_or_create(user=user)

    if profile.current_streak > profile.max_streak:
        profile.max_streak = profile.current_streak

    if profile.last_activity_date is None:
        next_streak = 1
    elif profile.last_activity_date == today:
        next_streak = profile.current_streak
    elif profile.last_activity_date == (today - timedelta(days=1)):
        next_streak = profile.current_streak + 1
    else:
        next_streak = 1

    profile.current_streak = next_streak
    profile.max_streak = max(profile.max_streak, next_streak)
    profile.last_activity_date = today
    profile.save(update_fields=['current_streak', 'max_streak', 'last_activity_date'])

    daily_activity, _ = UserDailyActivity.objects.select_for_update().get_or_create(
        user=user,
        activity_date=today,
        defaults={
            'points_earned': 0,
            'modules_completed': 0,
            'lessons_completed': 0,
            'challenges_completed': 0,
            'activity_score': 0,
        },
    )
    daily_activity.challenges_completed += max(0, int(challenges_completed or 0))
    daily_activity.lessons_completed += max(0, int(lessons_completed or 0))
    daily_activity.modules_completed += max(0, int(modules_completed or 0))
    daily_activity.points_earned += max(0, int(points_earned or 0))
    daily_activity.activity_score = _compute_daily_activity_score(activity=daily_activity)
    daily_activity.save(
        update_fields=[
            'challenges_completed',
            'lessons_completed',
            'modules_completed',
            'points_earned',
            'activity_score',
        ]
    )

    return profile, daily_activity


def register_challenge_completion_activity(user, *, points_earned=0):
    return _register_learning_activity(
        user,
        points_earned=points_earned,
        challenges_completed=1,
    )


def register_daily_challenge_completion_activity(user, *, points_earned=0):
    # Daily challenge completion contributes to the same streak and activity ledger.
    return _register_learning_activity(
        user,
        points_earned=points_earned,
        challenges_completed=1,
    )
