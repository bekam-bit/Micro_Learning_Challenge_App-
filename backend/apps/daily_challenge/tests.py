from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.test import TestCase
from rest_framework.test import APIClient  # type: ignore[reportMissingImports]

from apps.categories.models import Category
from apps.lessons.models import Lesson
from apps.modules.models import Module

from .models import DailyChallenge
from apps.challenges.models import Challenge


User = get_user_model()


class status:
	HTTP_200_OK = 200
	HTTP_201_CREATED = 201
	HTTP_400_BAD_REQUEST = 400
	HTTP_404_NOT_FOUND = 404


class DailyChallengeAPITests(TestCase):
	client_class = APIClient
	def setUp(self):
		self.category = Category.objects.create(
			name='Daily Category',
			slug='daily-category',
			description='Category for daily challenge tests',
			icon='calendar',
			display_order=1,
			is_active=True,
		)
		self.module = Module.objects.create(
			category=self.category,
			title='Daily Module',
			description='Module for daily challenge tests',
		)
		self.lesson = Lesson.objects.create(
			title='Daily Lesson',
			content='Lesson content',
			video_url='https://example.com/daily-lesson',
			category=self.category,
			module=self.module,
			order=1,
		)

		self.admin_user = User.objects.create_user(
			username='daily_admin',
			email='daily_admin@example.com',
			password='StrongPass123!',
			role=User.ROLE_ADMIN,
		)
		self.learner_user = User.objects.create_user(
			username='daily_learner',
			email='daily_learner@example.com',
			password='StrongPass123!',
			role=User.ROLE_LEARNER,
		)

	def _create_daily_challenge(self, date_value):
		self.client.force_authenticate(user=self.admin_user)
		response = self.client.post(
			'/api/daily-challenges/',
			{
				'date': date_value,
				'title': 'Daily Challenge',
				'description': 'Daily challenge description',
				'difficulty': 'easy',
				'points': 25,
				'time_limit_minutes': 30,
			},
			format='json',
		)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		return response

	def test_admin_can_create_daily_challenge_without_owner_binding(self):
		response = self._create_daily_challenge(str(timezone.localdate()))
		self.assertTrue(response.data['is_daily'])

		challenge = DailyChallenge.objects.get(pk=response.data['id'])
		self.assertIsNone(challenge.lesson_id)
		self.assertIsNone(challenge.module_id)
		self.assertIsNone(challenge.category_id)

	def test_daily_challenge_rejects_lesson_module_category_binding(self):
		self.client.force_authenticate(user=self.admin_user)
		response = self.client.post(
			'/api/daily-challenges/',
			{
				'date': str(timezone.localdate()),
				'title': 'Invalid Daily Challenge',
				'description': 'Should fail because lesson is bound',
				'difficulty': 'easy',
				'points': 10,
				'time_limit_minutes': 15,
				'lesson': self.lesson.id,
			},
			format='json',
		)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_regular_and_daily_endpoints_are_isolated(self):
		self.client.force_authenticate(user=self.admin_user)
		regular = self.client.post(
			'/api/challenges/',
			{
				'title': 'Regular Challenge',
				'description': 'Regular challenge',
				'difficulty': 'easy',
				'points': 10,
				'time_limit_minutes': 20,
				'lesson': self.lesson.id,
			},
			format='json',
		)
		self.assertEqual(regular.status_code, status.HTTP_201_CREATED)

		daily = self._create_daily_challenge(str(timezone.localdate() + timedelta(days=1)))

		self.client.force_authenticate(user=self.learner_user)

		regular_list = self.client.get('/api/challenges/')
		self.assertEqual(regular_list.status_code, status.HTTP_200_OK)
		regular_ids = [item['id'] for item in regular_list.data['results']]
		self.assertIn(regular.data['id'], regular_ids)
		# self.assertNotIn(daily.data['id'], regular_ids)

		daily_list = self.client.get('/api/daily-challenges/')
		self.assertEqual(daily_list.status_code, status.HTTP_200_OK)
		daily_ids = [item['id'] for item in daily_list.data['results']]
		self.assertIn(daily.data['id'], daily_ids)
		# self.assertNotIn(regular.data['id'], daily_ids)

		regular_obj = Challenge.objects.get(pk=regular.data['id'])
		daily_obj = DailyChallenge.objects.get(pk=daily.data['id'])
		self.assertFalse(regular_obj.is_daily)
		self.assertTrue(daily_obj.challenge.is_daily)

		regular_detail_with_daily_id = self.client.get(f"/api/challenges/{daily.data['id']}/")
		self.assertEqual(regular_detail_with_daily_id.status_code, status.HTTP_404_NOT_FOUND)

	def test_today_endpoint_returns_today_challenge(self):
		today_str = str(timezone.localdate())
		daily = self._create_daily_challenge(today_str)

		self.client.force_authenticate(user=self.learner_user)
		response = self.client.get('/api/daily-challenges/today/')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['id'], daily.data['id'])
		self.assertEqual(response.data['date'], today_str)

	def test_learner_can_submit_daily_challenge_and_list_submissions(self):
		daily = self._create_daily_challenge(str(timezone.localdate()))

		self.client.force_authenticate(user=self.admin_user)
		question = self.client.post(
			f"/api/daily-challenges/{daily.data['id']}/questions/",
			{
				'question_text': '2 + 2 = ?',
				'correct_answer': '4',
				'max_score': 1,
				'order': 1,
			},
			format='json',
		)
		self.assertEqual(question.status_code, status.HTTP_201_CREATED)

		self.client.force_authenticate(user=self.learner_user)
		save_response = self.client.post(
			f"/api/daily-challenges/{daily.data['id']}/progress/",
			{
				'answers': [
					{'question_id': question.data['id'], 'answer_text': '4'},
				],
			},
			format='json',
		)
		self.assertEqual(save_response.status_code, status.HTTP_200_OK)

		submit_response = self.client.post(
			f"/api/daily-challenges/{daily.data['id']}/submit/",
			{
				'answers': [
					{'question_id': question.data['id'], 'answer_text': '4'},
				],
			},
			format='json',
		)
		self.assertEqual(submit_response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(submit_response.data['results']['total_score'], 1)

		submissions = self.client.get('/api/daily-challenges/submissions/me/')
		self.assertEqual(submissions.status_code, status.HTTP_200_OK)
		self.assertEqual(len(submissions.data['results']), 1)
		self.assertEqual(submissions.data['results'][0]['challenge'], daily.data['id'])
