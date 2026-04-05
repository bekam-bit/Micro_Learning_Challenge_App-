from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from datetime import timedelta
from unittest.mock import patch
from rest_framework import status
from rest_framework.test import APITestCase

from apps.categories.models import Category
from apps.lessons.models import Lesson
from apps.modules.models import Module
from apps.progress.models import UserProgress
from apps.quiz.models import Quiz, QuizSubmission
from apps.users.models import UserDailyActivity, UserProfile
from apps.users.services import (
	register_challenge_completion_activity,
	register_daily_challenge_completion_activity,
)


TEST_LEARNER_USERNAME = "bekiyo1234"
TEST_LEARNER_EMAIL = "bekiyo@gmail.com"
TEST_LEARNER_PASSWORD = "beki@1234"

TEST_ADMIN_USERNAME = "admin_user"
TEST_ADMIN_EMAIL = "admin_user@example.com"
TEST_ADMIN_PASSWORD = "StrongPass123"


class UserProfileSignalTests(TestCase):
	def test_profile_is_auto_created_when_user_is_created(self):
		user_model = get_user_model()
		user = user_model.objects.create_user(
			username=TEST_LEARNER_USERNAME,
			email=TEST_LEARNER_EMAIL,
			password=TEST_LEARNER_PASSWORD,
		)

		self.assertTrue(UserProfile.objects.filter(user=user).exists())

	def test_admin_role_sets_is_staff_true(self):
		user_model = get_user_model()
		user = user_model.objects.create_user(
			username="admin_role_user",
			email="admin_role_user@example.com",
			password="StrongPass123",
			role="admin",
		)

		self.assertTrue(user.is_staff)

	def test_learner_role_sets_is_staff_false(self):
		user_model = get_user_model()
		user = user_model.objects.create_user(
			username="learner_role_user",
			email="learner_role_user@example.com",
			password="StrongPass123",
			role="learner",
		)

		self.assertFalse(user.is_staff)


class AuthApiTests(APITestCase):
	def test_register_creates_user_and_profile(self):
		payload = {
			"username": TEST_LEARNER_USERNAME,
			"email": TEST_LEARNER_EMAIL,
			"password": TEST_LEARNER_PASSWORD,
		}

		response = self.client.post(reverse("register"), payload, format="json")

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		user_model = get_user_model()
		user = user_model.objects.get(username=payload["username"])
		self.assertTrue(UserProfile.objects.filter(user=user).exists())

	def test_logout_blacklists_refresh_token(self):
		user_model = get_user_model()
		user_model.objects.create_user(
			username=TEST_LEARNER_USERNAME,
			email=TEST_LEARNER_EMAIL,
			password=TEST_LEARNER_PASSWORD,
		)

		login_response = self.client.post(
			reverse("login"),
			{"username": TEST_LEARNER_USERNAME, "password": TEST_LEARNER_PASSWORD},
			format="json",
		)

		self.assertEqual(login_response.status_code, status.HTTP_200_OK)
		access = login_response.data["access"]
		refresh = login_response.data["refresh"]

		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
		logout_response = self.client.post(
			reverse("logout"),
			{"refresh": refresh},
			format="json",
		)

		self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

		refresh_response = self.client.post(
			reverse("token_refresh"),
			{"refresh": refresh},
			format="json",
		)
		self.assertIn(
			refresh_response.status_code,
			(status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED),
		)

	def test_profile_contains_knowledge_momentum(self):
		user_model = get_user_model()
		user = user_model.objects.create_user(
			username=TEST_LEARNER_USERNAME,
			email=TEST_LEARNER_EMAIL,
			password=TEST_LEARNER_PASSWORD,
		)
		UserDailyActivity.objects.create(
			user=user,
			activity_date=user.date_joined.date(),
			activity_score=35,
		)

		login_response = self.client.post(
			reverse("login"),
			{"username": TEST_LEARNER_USERNAME, "password": TEST_LEARNER_PASSWORD},
			format="json",
		)
		self.assertEqual(login_response.status_code, status.HTTP_200_OK)

		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
		me_response = self.client.get(reverse("profile"), format="json")

		self.assertEqual(me_response.status_code, status.HTTP_200_OK)
		self.assertIn("knowledge_momentum", me_response.data)
		self.assertIn("days", me_response.data["knowledge_momentum"])

	def test_profile_includes_completed_module_lesson_quiz_totals(self):
		user_model = get_user_model()
		user = user_model.objects.create_user(
			username='aggregate_user',
			email='aggregate_user@example.com',
			password='StrongPass123',
		)

		category = Category.objects.create(name='Agg Cat', description='Aggregate category')
		module = Module.objects.create(
			category=category,
			title='Aggregate Module',
			description='Aggregate module',
		)
		lesson = Lesson.objects.create(
			title='Aggregate Lesson',
			content='Aggregate content',
			category=category,
			module=module,
			video_url='https://example.com/video.mp4',
			order=1,
		)
		quiz = Quiz.objects.create(title='Aggregate Quiz', lesson=lesson)

		UserProgress.objects.create(user=user, module=module, completed=True, completed_parts=1, total_parts=1)
		UserProgress.objects.create(user=user, lesson=lesson, completed=True, completed_parts=1, total_parts=1)
		QuizSubmission.objects.create(user=user, quiz=quiz, is_submitted=True, total_questions=1, correct_answers=1, score=100)

		login_response = self.client.post(
			reverse('login'),
			{'username': 'aggregate_user', 'password': 'StrongPass123'},
			format='json',
		)
		self.assertEqual(login_response.status_code, status.HTTP_200_OK)

		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
		me_response = self.client.get(reverse('profile'), format='json')

		self.assertEqual(me_response.status_code, status.HTTP_200_OK)
		self.assertEqual(me_response.data['total_modules_completed'], 1)
		self.assertEqual(me_response.data['total_lessons_completed'], 1)
		self.assertEqual(me_response.data['total_quizzes_completed'], 1)

	def test_non_admin_cannot_list_users(self):
		user_model = get_user_model()
		user_model.objects.create_user(
			username="learner_user",
			email="learner_user@example.com",
			password="StrongPass123",
		)

		login_response = self.client.post(
			reverse("login"),
			{"username": "learner_user", "password": "StrongPass123"},
			format="json",
		)
		self.assertEqual(login_response.status_code, status.HTTP_200_OK)

		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
		response = self.client.get(reverse("user_list"), format="json")
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_admin_can_list_users_and_update_user_role(self):
		user_model = get_user_model()
		admin_user = user_model.objects.create_user(
			username=TEST_ADMIN_USERNAME,
			email=TEST_ADMIN_EMAIL,
			password=TEST_ADMIN_PASSWORD,
			role="admin",
		)
		target_user = user_model.objects.create_user(
			username="target_user",
			email="target_user@example.com",
			password="StrongPass123",
		)

		login_response = self.client.post(
			reverse("login"),
			{"username": admin_user.username, "password": TEST_ADMIN_PASSWORD},
			format="json",
		)
		self.assertEqual(login_response.status_code, status.HTTP_200_OK)

		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")

		list_response = self.client.get(reverse("user_list"), format="json")
		self.assertEqual(list_response.status_code, status.HTTP_200_OK)

		update_response = self.client.patch(
			reverse("user_role_update", kwargs={"pk": target_user.id}),
			{"role": "admin"},
			format="json",
		)
		self.assertEqual(update_response.status_code, status.HTTP_200_OK)

		target_user.refresh_from_db()
		self.assertEqual(target_user.role, "admin")
		self.assertTrue(target_user.is_staff)

	def test_admin_user_list_includes_completed_aggregate_totals(self):
		user_model = get_user_model()
		admin_user = user_model.objects.create_user(
			username='aggregate_admin',
			email='aggregate_admin@example.com',
			password=TEST_ADMIN_PASSWORD,
			role='admin',
		)
		target_user = user_model.objects.create_user(
			username='aggregate_target',
			email='aggregate_target@example.com',
			password='StrongPass123',
		)

		category = Category.objects.create(name='Admin Agg Cat', description='Admin aggregate category')
		module = Module.objects.create(
			category=category,
			title='Admin Aggregate Module',
			description='Admin aggregate module',
		)
		lesson = Lesson.objects.create(
			title='Admin Aggregate Lesson',
			content='Admin aggregate content',
			category=category,
			module=module,
			video_url='https://example.com/admin-video.mp4',
			order=1,
		)
		quiz = Quiz.objects.create(title='Admin Aggregate Quiz', lesson=lesson)

		UserProgress.objects.create(user=target_user, module=module, completed=True, completed_parts=1, total_parts=1)
		UserProgress.objects.create(user=target_user, lesson=lesson, completed=True, completed_parts=1, total_parts=1)
		QuizSubmission.objects.create(
			user=target_user,
			quiz=quiz,
			is_submitted=True,
			total_questions=1,
			correct_answers=1,
			score=100,
		)

		login_response = self.client.post(
			reverse('login'),
			{'username': admin_user.username, 'password': TEST_ADMIN_PASSWORD},
			format='json',
		)
		self.assertEqual(login_response.status_code, status.HTTP_200_OK)

		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
		list_response = self.client.get(reverse('user_list'), format='json')
		self.assertEqual(list_response.status_code, status.HTTP_200_OK)

		target_payload = next(item for item in list_response.data if item['username'] == 'aggregate_target')
		self.assertEqual(target_payload['total_modules_completed'], 1)
		self.assertEqual(target_payload['total_lessons_completed'], 1)
		self.assertEqual(target_payload['total_quizzes_completed'], 1)

		detail_response = self.client.get(reverse('user_detail', kwargs={'pk': target_user.id}), format='json')
		self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
		self.assertEqual(detail_response.data['id'], target_user.id)
		self.assertEqual(detail_response.data['total_modules_completed'], 1)
		self.assertEqual(detail_response.data['total_lessons_completed'], 1)
		self.assertEqual(detail_response.data['total_quizzes_completed'], 1)

	def test_learner_cannot_self_promote_from_profile_endpoint(self):
		user_model = get_user_model()
		user_model.objects.create_user(
			username="self_promote_user",
			email="self_promote_user@example.com",
			password="StrongPass123",
			role="learner",
		)

		login_response = self.client.post(
			reverse("login"),
			{"username": "self_promote_user", "password": "StrongPass123"},
			format="json",
		)
		self.assertEqual(login_response.status_code, status.HTTP_200_OK)

		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
		patch_response = self.client.patch(
			reverse("profile"),
			{"role": "admin"},
			format="json",
		)
		self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

		user = user_model.objects.get(username="self_promote_user")
		self.assertEqual(user.role, "learner")
		self.assertFalse(user.is_staff)

	def test_cannot_demote_last_active_admin(self):
		user_model = get_user_model()
		admin_user = user_model.objects.create_user(
			username="single_admin",
			email="single_admin@example.com",
			password=TEST_ADMIN_PASSWORD,
			role="admin",
		)

		login_response = self.client.post(
			reverse("login"),
			{"username": admin_user.username, "password": TEST_ADMIN_PASSWORD},
			format="json",
		)
		self.assertEqual(login_response.status_code, status.HTTP_200_OK)

		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
		update_response = self.client.patch(
			reverse("user_role_update", kwargs={"pk": admin_user.id}),
			{"role": "learner"},
			format="json",
		)

		self.assertEqual(update_response.status_code, status.HTTP_400_BAD_REQUEST)
		admin_user.refresh_from_db()
		self.assertEqual(admin_user.role, "admin")

	@patch("apps.users.views.send_password_reset_email")
	def test_forgot_password_triggers_email_for_existing_user(self, send_reset_email_mock):
		user_model = get_user_model()
		user = user_model.objects.create_user(
			username="forgot_user",
			email="forgot_user@example.com",
			password="StrongPass123",
		)

		response = self.client.post(
			reverse("forgot_password"),
			{"email": user.email},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		send_reset_email_mock.assert_called_once_with(user)

	@patch("apps.users.views.send_password_reset_email")
	def test_forgot_password_does_not_disclose_unknown_email(self, send_reset_email_mock):
		response = self.client.post(
			reverse("forgot_password"),
			{"email": "unknown@example.com"},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		send_reset_email_mock.assert_not_called()

	def test_reset_password_confirm_updates_credentials(self):
		user_model = get_user_model()
		user = user_model.objects.create_user(
			username="reset_user",
			email="reset_user@example.com",
			password="OldStrongPass123",
		)

		uid = urlsafe_base64_encode(force_bytes(user.pk))
		token = default_token_generator.make_token(user)
		new_password = "NewStrongPass456"

		response = self.client.post(
			reverse("reset_password_confirm"),
			{
				"uid": uid,
				"token": token,
				"new_password": new_password,
				"confirm_password": new_password,
			},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)

		login_with_old_password = self.client.post(
			reverse("login"),
			{"username": user.username, "password": "OldStrongPass123"},
			format="json",
		)
		self.assertEqual(login_with_old_password.status_code, status.HTTP_401_UNAUTHORIZED)

		login_with_new_password = self.client.post(
			reverse("login"),
			{"username": user.username, "password": new_password},
			format="json",
		)
		self.assertEqual(login_with_new_password.status_code, status.HTTP_200_OK)

	def test_reset_password_confirm_rejects_invalid_token(self):
		user_model = get_user_model()
		user = user_model.objects.create_user(
			username="invalid_token_user",
			email="invalid_token_user@example.com",
			password="OldStrongPass123",
		)

		uid = urlsafe_base64_encode(force_bytes(user.pk))

		response = self.client.post(
			reverse("reset_password_confirm"),
			{
				"uid": uid,
				"token": "invalid-token",
				"new_password": "NewStrongPass456",
				"confirm_password": "NewStrongPass456",
			},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserStreakServiceTests(TestCase):
	def setUp(self):
		user_model = get_user_model()
		self.user = user_model.objects.create_user(
			username='streak_user',
			email='streak_user@example.com',
			password='StrongPass123',
		)
		self.other_user = user_model.objects.create_user(
			username='other_streak_user',
			email='other_streak_user@example.com',
			password='StrongPass123',
		)

	def test_register_challenge_completion_updates_streak_and_daily_activity(self):
		profile, activity = register_challenge_completion_activity(self.user, points_earned=15)

		self.assertEqual(profile.current_streak, 1)
		self.assertEqual(profile.max_streak, 1)
		self.assertEqual(profile.last_activity_date, activity.activity_date)
		self.assertEqual(activity.challenges_completed, 1)
		self.assertEqual(activity.points_earned, 15)
		self.assertGreater(activity.activity_score, 0)

	def test_same_day_completion_does_not_double_increment_streak(self):
		register_challenge_completion_activity(self.user, points_earned=10)
		profile, activity = register_challenge_completion_activity(self.user, points_earned=20)

		self.assertEqual(profile.current_streak, 1)
		self.assertEqual(profile.max_streak, 1)
		self.assertEqual(activity.challenges_completed, 2)
		self.assertEqual(activity.points_earned, 30)

	def test_gap_resets_streak_and_users_are_isolated(self):
		profile = UserProfile.objects.get(user=self.user)
		profile.current_streak = 4
		profile.last_activity_date = UserDailyActivity.objects.create(
			user=self.user,
			activity_date=timezone.localdate() - timedelta(days=3),
			activity_score=10,
		).activity_date
		profile.save(update_fields=['current_streak', 'last_activity_date'])

		register_challenge_completion_activity(self.user, points_earned=5)
		register_challenge_completion_activity(self.other_user, points_earned=8)

		profile.refresh_from_db()
		other_profile = UserProfile.objects.get(user=self.other_user)
		self.assertEqual(profile.current_streak, 1)
		self.assertEqual(profile.max_streak, 4)
		self.assertEqual(other_profile.current_streak, 1)
		self.assertEqual(other_profile.max_streak, 1)

	def test_daily_challenge_completion_uses_same_streak_pipeline(self):
		profile, activity = register_daily_challenge_completion_activity(self.user, points_earned=12)
		self.assertEqual(profile.current_streak, 1)
		self.assertEqual(profile.max_streak, 1)
		self.assertEqual(activity.challenges_completed, 1)
		self.assertEqual(activity.points_earned, 12)
