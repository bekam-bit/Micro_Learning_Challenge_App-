from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.challenges.models import Challenge, ChallengeSubmission
from apps.daily_challenge.models import DailyChallenge
from apps.lessons.models import Lesson
from apps.modules.models import Module
from apps.quiz.models.Quiz import Quiz

from .services import create_notification, notify_all_learners


@receiver(post_save, sender=DailyChallenge)
def notify_new_daily_challenge(sender, instance, created, **kwargs):
    if not created:
        return

    notify_all_learners(
        message=f'New daily challenge is available for {instance.date}: "{instance.title}".',
    )


@receiver(post_save, sender=ChallengeSubmission)
def notify_challenge_completion(sender, instance, created, **kwargs):
    if not created:
        return

    challenge_label = 'daily challenge' if instance.challenge.is_daily else 'challenge'
    points = instance.attempt.points_awarded if instance.attempt else 0
    create_notification(
        user=instance.user,
        message=f'Great job! You completed the {challenge_label} "{instance.challenge.title}" and earned {points} points.',
    )


@receiver(post_save, sender=Module)
def notify_new_module(sender, instance, created, **kwargs):
    if not created:
        return
    notify_all_learners(message=f'New content update: module "{instance.title}" is now available.')


@receiver(post_save, sender=Lesson)
def notify_new_lesson(sender, instance, created, **kwargs):
    if not created:
        return
    notify_all_learners(message=f'New content update: lesson "{instance.title}" has been added.')


@receiver(post_save, sender=Quiz)
def notify_new_quiz(sender, instance, created, **kwargs):
    if not created:
        return
    notify_all_learners(message=f'New content update: quiz "{instance.title}" is now available.')


@receiver(post_save, sender=Challenge)
def notify_new_challenge(sender, instance, created, **kwargs):
    if not created or instance.is_daily:
        return
    notify_all_learners(message=f'New content update: challenge "{instance.title}" is now available.')