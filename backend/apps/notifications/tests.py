from datetime import timedelta, date

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from apps.categories.models import Category
from apps.challenges.models import Challenge, ChallengeAttempt, ChallengeSubmission
from apps.daily_challenge.models import DailyChallenge
from apps.lessons.models import Lesson
from apps.modules.models import Module
from apps.quiz.models.Quiz import Quiz

from .models import Notification, NotificationRetentionSetting

User = get_user_model()


class NotificationModelTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username='notif_user',
			email='notif_user@example.com',
			password='StrongPass123!',
			role=User.ROLE_LEARNER,
		)

	def test_notification_defaults_to_unread(self):
		notification = Notification.objects.create(
			user=self.user,
			message='You have a new system update.',
		)

		self.assertFalse(notification.is_read)
		self.assertIsNotNone(notification.created_at)

	def test_notification_string_representation(self):
		notification = Notification.objects.create(
			user=self.user,
			message='Mandatory maintenance notice.',
		)

		self.assertIn(str(notification.id), str(notification))
		self.assertIn(str(self.user.id), str(notification))


class NotificationAutomationAndApiTests(APITestCase):
	def setUp(self):
		self.admin = User.objects.create_user(
			username='notif_admin',
			email='notif_admin@example.com',
			password='StrongPass123!',
			role=User.ROLE_ADMIN,
		)
		self.learner = User.objects.create_user(
			username='notif_learner',
			email='notif_learner@example.com',
			password='StrongPass123!',
			role=User.ROLE_LEARNER,
		)
		self.other_learner = User.objects.create_user(
			username='notif_other_learner',
			email='notif_other_learner@example.com',
			password='StrongPass123!',
			role=User.ROLE_LEARNER,
		)
		self.category = Category.objects.create(
			name='Notification Category',
			slug='notification-category',
			description='Notification category',
			icon='bell',
			display_order=1,
			is_active=True,
		)

	def test_daily_challenge_creation_notifies_learners(self):
		Notification.objects.all().delete()

		challenge = Challenge.objects.create(
    				title="Daily Test",
					description="Test Desc",
					difficulty="easy",
					is_daily=True
    # Add lesson/module/category if required by your model constraints
					)

# Then wrap it in DailyChallenge
		daily_challenge = DailyChallenge.objects.create(
			challenge=challenge,
			date=date.today()
		)

		learner_notifications = Notification.objects.filter(user=self.learner)
		other_learner_notifications = Notification.objects.filter(user=self.other_learner)

		self.assertEqual(learner_notifications.count(), 1)
		self.assertEqual(other_learner_notifications.count(), 1)
		self.assertIn('daily challenge', learner_notifications.first().message.lower())

	def test_challenge_completion_creates_user_notification(self):
		module = Module.objects.create(
			category=self.category,
			title='Notification Module',
			description='Module for notification tests',
		)
		lesson = Lesson.objects.create(
			title='Notification Lesson',
			content='Lesson content',
			video_url='https://example.com/notification-lesson',
			category=self.category,
			module=module,
			order=1,
		)
		challenge = Challenge.objects.create(
			title='Completion Challenge',
			description='Challenge completion notification test',
			difficulty='easy',
			points=25,
			time_limit_minutes=30,
			lesson=lesson,
		)

		attempt = ChallengeAttempt.objects.create(
			challenge=challenge,
			user=self.learner,
			is_submitted=True,
			points_awarded=20,
		)
		ChallengeSubmission.objects.create(
			challenge=challenge,
			user=self.learner,
			attempt=attempt,
			response_text='Done',
			status=ChallengeSubmission.STATUS_REVIEWED,
			score=1,
		)

		completion_note = Notification.objects.filter(
			user=self.learner,
			message__icontains='completed',
		).order_by('-id').first()
		self.assertIsNotNone(completion_note)
		self.assertIn('earned 20 points', completion_note.message)

	def test_new_content_creates_notifications(self):
		Notification.objects.all().delete()

		module = Module.objects.create(
			category=self.category,
			title='New Content Module',
			description='New module content',
		)
		lesson = Lesson.objects.create(
			title='New Content Lesson',
			content='Lesson content',
			video_url='https://example.com/new-content-lesson',
			category=self.category,
			module=module,
			order=1,
		)
		Quiz.objects.create(
			lesson=lesson,
			title='New Content Quiz',
			description='Quiz content',
		)

		learner_messages = list(Notification.objects.filter(user=self.learner).values_list('message', flat=True))
		self.assertTrue(any('module' in message.lower() for message in learner_messages))
		self.assertTrue(any('lesson' in message.lower() for message in learner_messages))
		self.assertTrue(any('quiz' in message.lower() for message in learner_messages))

	def test_notification_panel_list_and_mark_read_flow(self):
		note_1 = Notification.objects.create(user=self.learner, message='First notification')
		note_2 = Notification.objects.create(user=self.learner, message='Second notification')
		Notification.objects.create(user=self.other_learner, message='Other user notification')

		self.client.force_authenticate(user=self.learner)
		list_response = self.client.get('/api/notifications/')

		self.assertEqual(list_response.status_code, status.HTTP_200_OK)
		self.assertEqual(list_response.data['unread_count'], 2)
		self.assertEqual(len(list_response.data['results']), 2)

		mark_read_response = self.client.post(f'/api/notifications/{note_1.id}/read/')
		self.assertEqual(mark_read_response.status_code, status.HTTP_200_OK)

		note_1.refresh_from_db()
		self.assertTrue(note_1.is_read)
		note_2.refresh_from_db()
		self.assertFalse(note_2.is_read)

		mark_all_response = self.client.post('/api/notifications/read-all/')
		self.assertEqual(mark_all_response.status_code, status.HTTP_200_OK)
		self.assertEqual(mark_all_response.data['updated_count'], 1)

		note_2.refresh_from_db()
		self.assertTrue(note_2.is_read)

	def test_notification_list_includes_day_tags_for_ui(self):
		today_note = Notification.objects.create(user=self.learner, message='Today note')
		yesterday_note = Notification.objects.create(user=self.learner, message='Yesterday note')
		yesterday_time = timezone.now() - timedelta(days=1)
		Notification.objects.filter(pk=yesterday_note.pk).update(created_at=yesterday_time)

		self.client.force_authenticate(user=self.learner)
		response = self.client.get('/api/notifications/')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		items_by_id = {item['id']: item for item in response.data['results']}

		self.assertIn('day_bucket', items_by_id[today_note.id])
		self.assertIn('day_tag', items_by_id[today_note.id])
		self.assertIn('day_date', items_by_id[today_note.id])

		self.assertEqual(items_by_id[today_note.id]['day_bucket'], 'today')
		self.assertEqual(items_by_id[today_note.id]['day_tag'], 'Today')

		self.assertEqual(items_by_id[yesterday_note.id]['day_bucket'], 'yesterday')
		self.assertEqual(items_by_id[yesterday_note.id]['day_tag'], 'Yesterday')

	def test_user_cannot_mark_other_users_notification(self):
		other_note = Notification.objects.create(user=self.other_learner, message='Private note')

		self.client.force_authenticate(user=self.learner)
		response = self.client.post(f'/api/notifications/{other_note.id}/read/')

		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_retention_cleanup_uses_admin_defined_days(self):
		setting, _ = NotificationRetentionSetting.objects.get_or_create(singleton_key=1)
		setting.enabled = True
		setting.retention_days = 2
		setting.save(update_fields=['enabled', 'retention_days', 'updated_at'])

		old_read = Notification.objects.create(user=self.learner, message='old read')
		recent_read = Notification.objects.create(user=self.learner, message='recent read')
		old_unread = Notification.objects.create(user=self.learner, message='old unread')

		old_time = timezone.now() - timedelta(days=5)
		recent_time = timezone.now() - timedelta(days=1)

		Notification.objects.filter(pk=old_read.pk).update(is_read=True, created_at=old_time)
		Notification.objects.filter(pk=recent_read.pk).update(is_read=True, created_at=recent_time)
		Notification.objects.filter(pk=old_unread.pk).update(is_read=False, created_at=old_time)

		self.client.force_authenticate(user=self.learner)
		response = self.client.get('/api/notifications/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		self.assertFalse(Notification.objects.filter(pk=old_read.pk).exists())
		self.assertTrue(Notification.objects.filter(pk=recent_read.pk).exists())
		self.assertTrue(Notification.objects.filter(pk=old_unread.pk).exists())

	def test_retention_cleanup_can_be_disabled_by_admin(self):
		setting, _ = NotificationRetentionSetting.objects.get_or_create(singleton_key=1)
		setting.enabled = False
		setting.retention_days = 1
		setting.save(update_fields=['enabled', 'retention_days', 'updated_at'])

		old_read = Notification.objects.create(user=self.learner, message='old read preserved')
		old_time = timezone.now() - timedelta(days=10)
		Notification.objects.filter(pk=old_read.pk).update(is_read=True, created_at=old_time)

		self.client.force_authenticate(user=self.learner)
		response = self.client.get('/api/notifications/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertTrue(Notification.objects.filter(pk=old_read.pk).exists())
