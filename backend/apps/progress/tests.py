from datetime import timedelta

from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.categories.models import Category
from apps.challenges.models import Challenge, ChallengeAttempt, ChallengeAttemptAnswer, ChallengeQuestion
from apps.lessons.models import Lesson
from apps.modules.models import Module
from apps.progress.models import UserProgress
from apps.users.models import UserProfile


class UserProgressRollupTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		self.user = get_user_model().objects.create_user(
			username='learner',
			email='learner@example.com',
			password='Password123!',
		)
		self.client.force_authenticate(user=self.user)
		self.category = Category.objects.create(
			name='Python',
			description='Python tracks',
		)

	def _create_challenge_with_attempt(self, *, title, lesson=None, module=None, submitted=True):
		challenge = Challenge.objects.create(
			title=title,
			description='Challenge description',
			difficulty='easy',
			points=10,
			lesson=lesson,
			module=module,
			category=None,
		)
		question = ChallengeQuestion.objects.create(
			challenge=challenge,
			question_text='What is 2 + 2?',
			correct_answer='4',
			max_score=1,
			order=1,
		)
		attempt = ChallengeAttempt.objects.create(
			challenge=challenge,
			user=self.user,
			is_submitted=submitted,
			points_awarded=10 if submitted else 0,
		)
		ChallengeAttemptAnswer.objects.create(
			attempt=attempt,
			question=question,
			answer_text='4' if submitted else '',
			is_correct=submitted,
			score=1 if submitted else 0,
		)
		attempt.update_user_progress()
		return challenge

	def test_lesson_and_module_progress_roll_up_from_challenges(self):
		module = Module.objects.create(
			category=self.category,
			title='Module A',
			description='Module A description',
		)
		lesson = Lesson.objects.create(
			title='Lesson A1',
			content='Lesson content',
			category=self.category,
			module=module,
			order=1,
		)

		challenge_1 = self._create_challenge_with_attempt(
			title='Lesson Challenge 1',
			lesson=lesson,
			submitted=True,
		)

		lesson_progress = UserProgress.objects.get(user=self.user, lesson=lesson)
		self.assertEqual(lesson_progress.completed_parts, 1)
		self.assertEqual(lesson_progress.total_parts, 1)
		self.assertEqual(lesson_progress.progress_percent, 100)
		self.assertTrue(lesson_progress.completed)

		module_progress = UserProgress.objects.get(user=self.user, module=module)
		self.assertEqual(module_progress.completed_parts, 1)
		self.assertEqual(module_progress.total_parts, 1)
		self.assertEqual(module_progress.progress_percent, 100)
		self.assertTrue(module_progress.completed)

		challenge_progress = UserProgress.objects.get(user=self.user, challenge=challenge_1)
		self.assertEqual(challenge_progress.completed_parts, 1)
		self.assertEqual(challenge_progress.total_parts, 1)
		self.assertEqual(challenge_progress.progress_percent, 100)

	def test_module_progress_excludes_direct_module_challenges(self):
		module = Module.objects.create(
			category=self.category,
			title='Module B',
			description='Module B description',
		)

		self._create_challenge_with_attempt(
			title='Module Challenge 1',
			module=module,
			submitted=True,
		)
		self._create_challenge_with_attempt(
			title='Module Challenge 2',
			module=module,
			submitted=False,
		)

		module_progress = UserProgress.objects.get(user=self.user, module=module)
		self.assertEqual(module_progress.completed_parts, 0)
		self.assertEqual(module_progress.total_parts, 0)
		self.assertEqual(module_progress.progress_percent, 0)
		self.assertFalse(module_progress.completed)

	def test_profile_aggregates_sync_from_user_progress(self):
		module = Module.objects.create(
			category=self.category,
			title='Module C',
			description='Module C description',
		)
		lesson = Lesson.objects.create(
			title='Lesson C1',
			content='Lesson content',
			category=self.category,
			module=module,
			order=1,
		)

		self._create_challenge_with_attempt(
			title='Lesson Challenge C1',
			lesson=lesson,
			submitted=True,
		)

		profile = UserProfile.objects.get(user=self.user)
		self.assertEqual(profile.total_points, 10)
		self.assertEqual(profile.challenges_total_count, 1)
		self.assertEqual(profile.challenges_completed_count, 1)
		self.assertEqual(profile.lessons_total_count, 1)
		self.assertEqual(profile.lessons_completed_count, 1)
		self.assertEqual(profile.modules_total_count, 1)
		self.assertEqual(profile.modules_completed_count, 1)

	def test_progress_summary_endpoint_returns_expected_shape(self):
		module = Module.objects.create(
			category=self.category,
			title='Module D',
			description='Module D description',
		)
		lesson = Lesson.objects.create(
			title='Lesson D1',
			content='Lesson content',
			category=self.category,
			module=module,
			order=1,
		)
		self._create_challenge_with_attempt(
			title='Lesson Challenge D1',
			lesson=lesson,
			submitted=True,
		)

		response = self.client.get(reverse('user_progress_summary'))
		self.assertEqual(response.status_code, 200)
		self.assertIn('challenges', response.data)
		self.assertIn('lessons', response.data)
		self.assertIn('modules', response.data)
		self.assertEqual(response.data['points_earned'], 10)

	def test_progress_list_endpoint_supports_owner_type_filter(self):
		module = Module.objects.create(
			category=self.category,
			title='Module E',
			description='Module E description',
		)
		lesson = Lesson.objects.create(
			title='Lesson E1',
			content='Lesson content',
			category=self.category,
			module=module,
			order=1,
		)
		self._create_challenge_with_attempt(
			title='Lesson Challenge E1',
			lesson=lesson,
			submitted=True,
		)

		response = self.client.get(reverse('user_progress_list'), {'owner_type': 'lesson'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]['owner_type'], 'lesson')

	def test_progress_summary_query_count_budget(self):
		module = Module.objects.create(
			category=self.category,
			title='Perf Module',
			description='Perf Module description',
		)
		lesson = Lesson.objects.create(
			title='Perf Lesson',
			content='Perf content',
			category=self.category,
			module=module,
			order=1,
		)
		self._create_challenge_with_attempt(
			title='Perf Challenge',
			lesson=lesson,
			submitted=True,
		)

		with CaptureQueriesContext(connection) as ctx:
			response = self.client.get(reverse('user_progress_summary'))

		self.assertEqual(response.status_code, 200)
		# Budget guardrail: summary endpoint should stay low-query.
		self.assertLessEqual(len(ctx), 5)


class AdminUserProgressApiTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		User = get_user_model()
		self.admin_user = User.objects.create_user(
			username='admin-user',
			email='admin@example.com',
			password='Password123!',
			role='admin',
		)
		self.learner_one = User.objects.create_user(
			username='learner-one',
			email='learner1@example.com',
			password='Password123!',
		)
		self.learner_two = User.objects.create_user(
			username='learner-two',
			email='learner2@example.com',
			password='Password123!',
		)

	def test_admin_can_list_all_users_progress(self):
		UserProgress.objects.create(
			user=self.learner_one,
			lesson=Lesson.objects.create(
				title='L1',
				content='Lesson 1',
				category=Category.objects.create(name='Cat 1', description='Cat 1 desc'),
			),
			completed=True,
			completed_parts=1,
			total_parts=1,
		)
		UserProgress.objects.create(
			user=self.learner_two,
			module=Module.objects.create(
				title='M1',
				description='Module 1',
				category=Category.objects.create(name='Cat 2', description='Cat 2 desc'),
			),
			completed=False,
			completed_parts=0,
			total_parts=2,
		)

		self.client.force_authenticate(user=self.admin_user)
		response = self.client.get(reverse('admin_user_progress_list'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['count'], 2)
		self.assertEqual(len(response.data['results']), 2)
		self.assertIn('user_id', response.data['results'][0])
		self.assertIn('username', response.data['results'][0])
		self.assertIn('email', response.data['results'][0])

	def test_admin_list_supports_search_and_ordering(self):
		lesson = Lesson.objects.create(
			title='Search Lesson',
			content='Lesson content',
			category=Category.objects.create(name='Search Cat', description='Search Cat desc'),
		)
		challenge_alpha = Challenge.objects.create(
			title='Alpha Challenge',
			description='Alpha',
			difficulty='easy',
			lesson=lesson,
		)
		challenge_beta = Challenge.objects.create(
			title='Beta Challenge',
			description='Beta',
			difficulty='easy',
			lesson=lesson,
		)
		UserProgress.objects.create(
			user=self.learner_one,
			challenge=challenge_alpha,
			completed=True,
			points_earned=15,
			completed_parts=1,
			total_parts=1,
		)
		UserProgress.objects.create(
			user=self.learner_two,
			challenge=challenge_beta,
			completed=True,
			points_earned=30,
			completed_parts=1,
			total_parts=1,
		)

		self.client.force_authenticate(user=self.admin_user)
		response = self.client.get(
			reverse('admin_user_progress_list'),
			{'search': 'beta', 'ordering': '-points_earned'},
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['count'], 1)
		self.assertEqual(response.data['results'][0]['owner_title'], 'Beta Challenge')

	def test_admin_list_supports_pagination(self):
		lesson = Lesson.objects.create(
			title='Page Lesson',
			content='Lesson content',
			category=Category.objects.create(name='Page Cat', description='Page Cat desc'),
		)
		for index in range(5):
			UserProgress.objects.create(
				user=self.learner_one,
				challenge=Challenge.objects.create(
					title=f'Challenge {index}',
					description='Challenge',
					difficulty='easy',
					lesson=lesson,
				),
				completed=False,
				completed_parts=0,
				total_parts=1,
			)

		self.client.force_authenticate(user=self.admin_user)
		response = self.client.get(reverse('admin_user_progress_list'), {'page_size': 2, 'page': 1})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['count'], 5)
		self.assertEqual(len(response.data['results']), 2)
		self.assertIsNotNone(response.data['next'])

	def test_non_admin_cannot_list_all_users_progress(self):
		self.client.force_authenticate(user=self.learner_one)
		response = self.client.get(reverse('admin_user_progress_list'))
		self.assertEqual(response.status_code, 403)

	def test_admin_summary_returns_expected_payload(self):
		lesson = Lesson.objects.create(
			title='L2',
			content='Lesson 2',
			category=Category.objects.create(name='Cat 3', description='Cat 3 desc'),
		)
		module = Module.objects.create(
			title='M2',
			description='Module 2',
			category=Category.objects.create(name='Cat 4', description='Cat 4 desc'),
		)

		UserProgress.objects.create(
			user=self.learner_one,
			challenge=Challenge.objects.create(
				title='C1',
				description='Challenge 1',
				difficulty='easy',
				lesson=lesson,
			),
			completed=True,
			points_earned=25,
			completed_parts=1,
			total_parts=1,
		)
		UserProgress.objects.create(
			user=self.learner_two,
			module=module,
			completed=False,
			completed_parts=0,
			total_parts=3,
		)

		self.client.force_authenticate(user=self.admin_user)
		response = self.client.get(reverse('admin_user_progress_summary'))

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['users_tracked'], 2)
		self.assertEqual(response.data['challenges']['total'], 1)
		self.assertEqual(response.data['challenges']['completed'], 1)
		self.assertEqual(response.data['modules']['total'], 1)
		self.assertEqual(response.data['modules']['completed'], 0)
		self.assertEqual(response.data['points_earned'], 25)

	def test_non_admin_cannot_access_admin_summary(self):
		self.client.force_authenticate(user=self.learner_one)
		response = self.client.get(reverse('admin_user_progress_summary'))
		self.assertEqual(response.status_code, 403)

	def test_admin_summary_supports_date_range_filter(self):
		lesson = Lesson.objects.create(
			title='L3',
			content='Lesson 3',
			category=Category.objects.create(name='Cat 5', description='Cat 5 desc'),
		)

		older = UserProgress.objects.create(
			user=self.learner_one,
			challenge=Challenge.objects.create(
				title='C-old',
				description='Old challenge',
				difficulty='easy',
				lesson=lesson,
			),
			completed=True,
			points_earned=10,
			completed_parts=1,
			total_parts=1,
		)
		recent = UserProgress.objects.create(
			user=self.learner_two,
			challenge=Challenge.objects.create(
				title='C-new',
				description='New challenge',
				difficulty='easy',
				lesson=lesson,
			),
			completed=True,
			points_earned=20,
			completed_parts=1,
			total_parts=1,
		)

		now = timezone.now()
		UserProgress.objects.filter(pk=older.pk).update(updated_at=now - timedelta(days=3))
		UserProgress.objects.filter(pk=recent.pk).update(updated_at=now)

		self.client.force_authenticate(user=self.admin_user)
		response = self.client.get(reverse('admin_user_progress_summary'), {'from': (now - timedelta(days=1)).date().isoformat()})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['users_tracked'], 1)
		self.assertEqual(response.data['challenges']['total'], 1)
		self.assertEqual(response.data['points_earned'], 20)

	def test_admin_summary_query_count_budget(self):
		lesson = Lesson.objects.create(
			title='Perf Admin Lesson',
			content='Perf admin content',
			category=Category.objects.create(name='Perf Admin Cat', description='Perf admin cat desc'),
		)
		UserProgress.objects.create(
			user=self.learner_one,
			challenge=Challenge.objects.create(
				title='Perf Admin Challenge',
				description='Perf',
				difficulty='easy',
				lesson=lesson,
			),
			completed=True,
			points_earned=10,
			completed_parts=1,
			total_parts=1,
		)

		self.client.force_authenticate(user=self.admin_user)
		with CaptureQueriesContext(connection) as ctx:
			response = self.client.get(reverse('admin_user_progress_summary'))

		self.assertEqual(response.status_code, 200)
		# Budget guardrail: aggregate + users tracked should remain compact.
		self.assertLessEqual(len(ctx), 6)
