from django.contrib.auth import get_user_model
from datetime import timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.categories.models import Category
from apps.lessons.models import Lesson
from apps.modules.models import Module
from apps.users.models import UserDailyActivity, UserProfile

from .models import ChallengeAttempt, ChallengeQuestion, ChallengeSubmission


User = get_user_model()


class ChallengeAPITests(APITestCase):
	def setUp(self):
		self.category = Category.objects.create(
			name='Programming',
			slug='programming',
			description='Programming category',
			icon='code',
			display_order=1,
			is_active=True,
		)
		self.module = Module.objects.create(
			category=self.category,
			title='Python Basics',
			description='Core python module',
		)
		self.lesson = Lesson.objects.create(
			title='Variables',
			content='Lesson content',
			video_url='https://example.com/video',
			category=self.category,
			module=self.module,
			order=1,
		)

		self.admin_user = User.objects.create_user(
			username='challenge_admin',
			email='challenge_admin@example.com',
			password='StrongPass123!',
			role=User.ROLE_ADMIN,
		)
		self.learner_user = User.objects.create_user(
			username='challenge_learner',
			email='challenge_learner@example.com',
			password='StrongPass123!',
			role=User.ROLE_LEARNER,
		)

	def test_admin_can_create_challenge(self):
		self.client.force_authenticate(user=self.admin_user)
		payload = {
			'title': 'Variable Match',
			'description': 'Solve variable challenge',
			'difficulty': 'easy',
			'points': 20,
			'time_limit_minutes': 30,
			'lesson': self.lesson.id,
		}

		response = self.client.post('/api/challenges/', payload, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_learner_cannot_create_challenge(self):
		self.client.force_authenticate(user=self.learner_user)
		payload = {
			'title': 'Unauthorized Challenge',
			'description': 'Should fail',
			'difficulty': 'easy',
			'points': 10,
			'time_limit_minutes': 30,
			'lesson': self.lesson.id,
		}

		response = self.client.post('/api/challenges/', payload, format='json')
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_public_can_view_challenges(self):
		self.client.force_authenticate(user=self.admin_user)
		create_response = self.client.post(
			'/api/challenges/',
			{
				'title': 'Public Challenge',
				'description': 'Visible challenge',
				'difficulty': 'medium',
				'points': 30,
				'time_limit_minutes': 30,
				'module': self.module.id,
			},
			format='json',
		)
		self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
		self.client.force_authenticate(user=None)

		response = self.client.get('/api/challenges/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['results'][0]['scope'], 'module')

		questions_response = self.client.get(f"/api/challenges/{create_response.data['id']}/questions/")
		self.assertEqual(questions_response.status_code, status.HTTP_200_OK)

	def test_challenge_list_defaults_to_latest_first(self):
		self.client.force_authenticate(user=self.admin_user)
		older = self.client.post(
			'/api/challenges/',
			{
				'title': 'Older Challenge',
				'description': 'Created first',
				'difficulty': 'easy',
				'points': 10,
				'time_limit_minutes': 10,
				'lesson': self.lesson.id,
			},
			format='json',
		)
		newer = self.client.post(
			'/api/challenges/',
			{
				'title': 'Newer Challenge',
				'description': 'Created second',
				'difficulty': 'medium',
				'points': 20,
				'time_limit_minutes': 10,
				'lesson': self.lesson.id,
			},
			format='json',
		)

		self.assertEqual(older.status_code, status.HTTP_201_CREATED)
		self.assertEqual(newer.status_code, status.HTTP_201_CREATED)

		self.client.force_authenticate(user=None)
		response = self.client.get('/api/challenges/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['results'][0]['id'], newer.data['id'])
		self.assertEqual(response.data['results'][1]['id'], older.data['id'])

	def test_admin_can_add_questions(self):
		self.client.force_authenticate(user=self.admin_user)
		challenge_response = self.client.post(
			'/api/challenges/',
			{
				'title': 'Questioned Challenge',
				'description': 'Admin sets answer key',
				'difficulty': 'medium',
				'points': 25,
				'time_limit_minutes': 15,
				'lesson': self.lesson.id,
			},
			format='json',
		)
		self.assertEqual(challenge_response.status_code, status.HTTP_201_CREATED)

		question_response = self.client.post(
			f"/api/challenges/{challenge_response.data['id']}/questions/",
			{
				'question_text': 'What keyword declares a variable in Python?',
				'correct_answer': 'No keyword',
				'explanation': 'Python assigns using = and does not use var/let style keywords.',
				'max_score': 2,
				'order': 1,
			},
			format='json',
		)
		self.assertEqual(question_response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(question_response.data['max_score'], 2)
		self.assertEqual(
			question_response.data['explanation'],
			'Python assigns using = and does not use var/let style keywords.',
		)

		self.client.force_authenticate(user=self.learner_user)
		list_response = self.client.get(f"/api/challenges/{challenge_response.data['id']}/questions/")
		self.assertEqual(list_response.status_code, status.HTTP_200_OK)
		self.assertIn('answer_format', list_response.data['results'][0])

		challenge_detail_as_learner = self.client.get(f"/api/challenges/{challenge_response.data['id']}/")
		self.assertEqual(challenge_detail_as_learner.status_code, status.HTTP_200_OK)
		self.assertIn('questions', challenge_detail_as_learner.data)
		self.assertEqual(len(challenge_detail_as_learner.data['questions']), 1)
		self.assertNotIn('correct_answer', challenge_detail_as_learner.data['questions'][0])

		self.client.force_authenticate(user=self.admin_user)
		challenge_detail_as_admin = self.client.get(f"/api/challenges/{challenge_response.data['id']}/")
		self.assertEqual(challenge_detail_as_admin.status_code, status.HTTP_200_OK)
		self.assertIn('questions', challenge_detail_as_admin.data)
		self.assertEqual(challenge_detail_as_admin.data['questions'][0]['correct_answer'], 'No keyword')

	def test_learner_can_save_progress_and_submit_with_auto_grading(self):
		self.client.force_authenticate(user=self.admin_user)
		challenge_response = self.client.post(
			'/api/challenges/',
			{
				'title': 'Submission Challenge',
				'description': 'Submit answer',
				'difficulty': 'hard',
				'points': 50,
				'time_limit_minutes': 30,
				'category': self.category.id,
			},
			format='json',
		)
		self.assertEqual(challenge_response.status_code, status.HTTP_201_CREATED)
		challenge_id = challenge_response.data['id']
		question_1 = self.client.post(
			f'/api/challenges/{challenge_id}/questions/',
			{
				'question_text': '2 + 2 = ?',
				'correct_answer': '4',
				'explanation': 'Adding two and two gives four.',
				'max_score': 1,
				'order': 1,
			},
			format='json',
		)
		question_2 = self.client.post(
			f'/api/challenges/{challenge_id}/questions/',
			{
				'question_text': 'Capital of Ethiopia?',
				'correct_answer': 'Addis Ababa',
				'explanation': 'Addis Ababa is the capital city of Ethiopia.',
				'max_score': 1,
				'order': 2,
			},
			format='json',
		)
		self.assertEqual(question_1.status_code, status.HTTP_201_CREATED)
		self.assertEqual(question_2.status_code, status.HTTP_201_CREATED)

		self.client.force_authenticate(user=self.learner_user)
		progress_response = self.client.post(
			f'/api/challenges/{challenge_id}/progress/',
			{
				'answers': [
					{'question_id': question_1.data['id'], 'answer_text': '4'},
				],
			},
			format='json',
		)
		self.assertEqual(progress_response.status_code, status.HTTP_200_OK)
		self.assertNotIn('correct_answer_value', progress_response.data['answers'][0])
		self.assertNotIn('explanation', progress_response.data['answers'][0])

		submit_response = self.client.post(
			f'/api/challenges/{challenge_id}/submit/',
			{
				'answers': [
					{'question_id': question_1.data['id'], 'answer_text': '4'},
					{'question_id': question_2.data['id'], 'answer_text': 'Addis Ababa'},
				],
			},
			format='json',
		)
		self.assertEqual(submit_response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(submit_response.data['points_awarded'], 50)
		self.assertEqual(submit_response.data['results']['answers'][0]['correct_answer_value'], '4')
		self.assertEqual(submit_response.data['results']['answers'][0]['explanation'], 'Adding two and two gives four.')
		submission = ChallengeSubmission.objects.get(challenge_id=challenge_id, user=self.learner_user)
		self.assertEqual(submission.score, 2)

	def test_admin_cannot_submit_challenge_response(self):
		self.client.force_authenticate(user=self.admin_user)
		challenge_response = self.client.post(
			'/api/challenges/',
			{
				'title': 'Admin Submit Restriction',
				'description': 'Admin should not submit',
				'difficulty': 'easy',
				'points': 15,
				'time_limit_minutes': 30,
				'lesson': self.lesson.id,
			},
			format='json',
		)
		self.assertEqual(challenge_response.status_code, status.HTTP_201_CREATED)

		submit_response = self.client.post(
			f"/api/challenges/{challenge_response.data['id']}/submit/",
			{'answers': []},
			format='json',
		)
		self.assertEqual(submit_response.status_code, status.HTTP_403_FORBIDDEN)

	def test_late_submission_denies_points_and_keeps_saved_progress(self):
		self.client.force_authenticate(user=self.admin_user)
		challenge_response = self.client.post(
			'/api/challenges/',
			{
				'title': 'Timed Challenge',
				'description': 'Must be completed quickly',
				'difficulty': 'hard',
				'points': 100,
				'time_limit_minutes': 1,
				'lesson': self.lesson.id,
			},
			format='json',
		)
		challenge_id = challenge_response.data['id']
		question_response = self.client.post(
			f'/api/challenges/{challenge_id}/questions/',
			{
				'question_text': 'Type YES',
				'correct_answer': 'YES',
				'explanation': 'This checks simple exact match input.',
				'max_score': 1,
				'order': 1,
			},
			format='json',
		)

		self.client.force_authenticate(user=self.learner_user)
		save_response = self.client.post(
			f'/api/challenges/{challenge_id}/progress/',
			{
				'answers': [
					{'question_id': question_response.data['id'], 'answer_text': 'YES'},
				]
			},
			format='json',
		)
		self.assertEqual(save_response.status_code, status.HTTP_200_OK)

		attempt = ChallengeAttempt.objects.get(challenge_id=challenge_id, user=self.learner_user)
		attempt.deadline_at = timezone.now() - timedelta(minutes=1)
		attempt.save(update_fields=['deadline_at'])

		late_progress = self.client.post(
			f'/api/challenges/{challenge_id}/progress/',
			{
				'answers': [
					{'question_id': question_response.data['id'], 'answer_text': 'NO'},
				]
			},
			format='json',
		)
		self.assertEqual(late_progress.status_code, status.HTTP_400_BAD_REQUEST)

		late_submit = self.client.post(
			f'/api/challenges/{challenge_id}/submit/',
			{
				'answers': [
					{'question_id': question_response.data['id'], 'answer_text': 'YES'},
				]
			},
			format='json',
		)
		self.assertEqual(late_submit.status_code, status.HTTP_201_CREATED)
		self.assertFalse(late_submit.data['within_time_limit'])
		self.assertEqual(late_submit.data['points_awarded'], 0)

	def test_admin_can_create_all_supported_question_types(self):
		self.client.force_authenticate(user=self.admin_user)
		challenge_response = self.client.post(
			'/api/challenges/',
			{
				'title': 'All Types Challenge',
				'description': 'Covers supported validation types',
				'difficulty': 'medium',
				'points': 20,
				'time_limit_minutes': 20,
				'lesson': self.lesson.id,
			},
			format='json',
		)
		challenge_id = challenge_response.data['id']

		payloads = [
			{
				'question_text': 'Single choice sample',
				'question_type': 'single_choice',
				'options': ['A', 'B', 'C'],
				'correct_answer': 'B',
				'max_score': 1,
				'order': 1,
			},
			{
				'question_text': 'Multiple choice sample',
				'question_type': 'multiple_choice',
				'options': ['A', 'B', 'C'],
				'correct_options': ['A', 'C'],
				'correct_answer': 'A,C',
				'max_score': 1,
				'order': 2,
			},
			{
				'question_text': 'True or false sample',
				'question_type': 'true_false',
				'correct_answer': 'true',
				'max_score': 1,
				'order': 3,
			},
			{
				'question_text': 'Numeric sample',
				'question_type': 'numeric',
				'correct_answer': '3.14',
				'numeric_tolerance': 0.01,
				'max_score': 1,
				'order': 4,
			},
			{
				'question_text': 'Strict text sample',
				'question_type': 'short_text_strict',
				'correct_answer': 'Addis Ababa',
				'max_score': 1,
				'order': 5,
			},
		]

		for payload in payloads:
			response = self.client.post(
				f'/api/challenges/{challenge_id}/questions/',
				payload,
				format='json',
			)
			self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_type_specific_auto_grading_for_requested_types(self):
		self.client.force_authenticate(user=self.admin_user)
		challenge_response = self.client.post(
			'/api/challenges/',
			{
				'title': 'Type Grading Challenge',
				'description': 'Validate grading logic by type',
				'difficulty': 'hard',
				'points': 30,
				'time_limit_minutes': 20,
				'lesson': self.lesson.id,
			},
			format='json',
		)
		challenge_id = challenge_response.data['id']

		single = self.client.post(
			f'/api/challenges/{challenge_id}/questions/',
			{
				'question_text': 'Choose B',
				'question_type': 'single_choice',
				'options': ['A', 'B'],
				'correct_answer': 'B',
				'max_score': 1,
				'order': 1,
			},
			format='json',
		)
		multiple = self.client.post(
			f'/api/challenges/{challenge_id}/questions/',
			{
				'question_text': 'Choose A and C',
				'question_type': 'multiple_choice',
				'options': ['A', 'B', 'C'],
				'correct_options': ['A', 'C'],
				'correct_answer': 'A,C',
				'max_score': 1,
				'order': 2,
			},
			format='json',
		)
		true_false = self.client.post(
			f'/api/challenges/{challenge_id}/questions/',
			{
				'question_text': 'Python is case-sensitive',
				'question_type': 'true_false',
				'correct_answer': 'true',
				'max_score': 1,
				'order': 3,
			},
			format='json',
		)
		numeric = self.client.post(
			f'/api/challenges/{challenge_id}/questions/',
			{
				'question_text': 'Pi (2 d.p.)',
				'question_type': 'numeric',
				'correct_answer': '3.14',
				'numeric_tolerance': 0.01,
				'max_score': 1,
				'order': 4,
			},
			format='json',
		)
		strict_text = self.client.post(
			f'/api/challenges/{challenge_id}/questions/',
			{
				'question_text': 'Capital of Ethiopia',
				'question_type': 'short_text_strict',
				'correct_answer': 'Addis Ababa',
				'max_score': 1,
				'order': 5,
			},
			format='json',
		)

		self.client.force_authenticate(user=self.learner_user)
		submit_response = self.client.post(
			f'/api/challenges/{challenge_id}/submit/',
			{
				'answers': [
					{'question_id': single.data['id'], 'answer_text': 'B'},
					{'question_id': multiple.data['id'], 'answer_options': ['C', 'A']},
					{'question_id': true_false.data['id'], 'answer_boolean': True},
					{'question_id': numeric.data['id'], 'answer_number': 3.141},
					{'question_id': strict_text.data['id'], 'answer_text': 'addis ababa'},
				],
			},
			format='json',
		)

		self.assertEqual(submit_response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(submit_response.data['score'], 5)
		self.assertEqual(submit_response.data['points_awarded'], 30)

	def test_partial_score_gets_proportional_points(self):
		self.client.force_authenticate(user=self.admin_user)
		challenge_response = self.client.post(
			'/api/challenges/',
			{
				'title': 'Proportional Points Challenge',
				'description': 'Points scale with score percentage',
				'difficulty': 'medium',
				'points': 40,
				'time_limit_minutes': 15,
				'lesson': self.lesson.id,
			},
			format='json',
		)
		challenge_id = challenge_response.data['id']

		q1 = self.client.post(
			f'/api/challenges/{challenge_id}/questions/',
			{
				'question_text': '1 + 1',
				'question_type': 'short_text_strict',
				'correct_answer': '2',
				'max_score': 1,
				'order': 1,
			},
			format='json',
		)
		q2 = self.client.post(
			f'/api/challenges/{challenge_id}/questions/',
			{
				'question_text': '2 + 2',
				'question_type': 'short_text_strict',
				'correct_answer': '4',
				'max_score': 1,
				'order': 2,
			},
			format='json',
		)

		self.client.force_authenticate(user=self.learner_user)
		submit_response = self.client.post(
			f'/api/challenges/{challenge_id}/submit/',
			{
				'answers': [
					{'question_id': q1.data['id'], 'answer_text': '2'},
					{'question_id': q2.data['id'], 'answer_text': '0'},
				],
			},
			format='json',
		)

		self.assertEqual(submit_response.status_code, status.HTTP_201_CREATED)
		self.assertEqual(submit_response.data['score'], 1)
		self.assertEqual(submit_response.data['max_score'], 2)
		self.assertEqual(submit_response.data['points_awarded'], 20)
		self.assertEqual(submit_response.data['submission_timing_status'], 'on_time')
		self.assertIsNotNone(submit_response.data['completion_time_seconds'])

	def test_second_submit_is_blocked_after_first_submit(self):
		self.client.force_authenticate(user=self.admin_user)
		challenge_response = self.client.post(
			'/api/challenges/',
			{
				'title': 'Duplicate Submit Challenge',
				'description': 'Should not accept second submit',
				'difficulty': 'easy',
				'points': 10,
				'time_limit_minutes': 10,
				'lesson': self.lesson.id,
			},
			format='json',
		)
		challenge_id = challenge_response.data['id']

		question = self.client.post(
			f'/api/challenges/{challenge_id}/questions/',
			{
				'question_text': 'Type OK',
				'question_type': 'short_text_strict',
				'correct_answer': 'OK',
				'max_score': 1,
				'order': 1,
			},
			format='json',
		)

		self.client.force_authenticate(user=self.learner_user)
		first_submit = self.client.post(
			f'/api/challenges/{challenge_id}/submit/',
			{
				'answers': [
					{'question_id': question.data['id'], 'answer_text': 'OK'},
				],
			},
			format='json',
		)
		self.assertEqual(first_submit.status_code, status.HTTP_201_CREATED)

		second_submit = self.client.post(
			f'/api/challenges/{challenge_id}/submit/',
			{
				'answers': [
					{'question_id': question.data['id'], 'answer_text': 'OK'},
				],
			},
			format='json',
		)
		self.assertEqual(second_submit.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertEqual(second_submit.data['detail'], 'Challenge is already submitted.')

	def test_submit_with_same_idempotency_key_replays_prior_response(self):
		self.client.force_authenticate(user=self.admin_user)
		challenge_response = self.client.post(
			'/api/challenges/',
			{
				'title': 'Idempotent Submit Challenge',
				'description': 'Repeated request should replay result',
				'difficulty': 'easy',
				'points': 20,
				'time_limit_minutes': 10,
				'lesson': self.lesson.id,
			},
			format='json',
		)
		challenge_id = challenge_response.data['id']

		question = self.client.post(
			f'/api/challenges/{challenge_id}/questions/',
			{
				'question_text': 'Type GO',
				'question_type': 'short_text_strict',
				'correct_answer': 'GO',
				'max_score': 1,
				'order': 1,
			},
			format='json',
		)

		self.client.force_authenticate(user=self.learner_user)
		first_submit = self.client.post(
			f'/api/challenges/{challenge_id}/submit/',
			{
				'answers': [
					{'question_id': question.data['id'], 'answer_text': 'GO'},
				],
			},
			format='json',
			HTTP_X_IDEMPOTENCY_KEY='submit-key-001',
		)
		self.assertEqual(first_submit.status_code, status.HTTP_201_CREATED)
		self.assertFalse(first_submit.data['idempotency_replayed'])

		retry_submit = self.client.post(
			f'/api/challenges/{challenge_id}/submit/',
			{
				'answers': [
					{'question_id': question.data['id'], 'answer_text': 'WRONG'},
				],
			},
			format='json',
			HTTP_X_IDEMPOTENCY_KEY='submit-key-001',
		)
		self.assertEqual(retry_submit.status_code, status.HTTP_200_OK)
		self.assertTrue(retry_submit.data['idempotency_replayed'])
		self.assertEqual(retry_submit.data['id'], first_submit.data['id'])
		self.assertEqual(retry_submit.data['score'], first_submit.data['score'])

	def test_first_challenge_completion_starts_streak(self):
		self.client.force_authenticate(user=self.admin_user)
		challenge_response = self.client.post(
			'/api/challenges/',
			{
				'title': 'Streak Start Challenge',
				'description': 'Starts streak',
				'difficulty': 'easy',
				'points': 10,
				'time_limit_minutes': 10,
				'lesson': self.lesson.id,
			},
			format='json',
		)
		challenge_id = challenge_response.data['id']
		question = self.client.post(
			f'/api/challenges/{challenge_id}/questions/',
			{
				'question_text': 'Type YES',
				'question_type': 'short_text_strict',
				'correct_answer': 'YES',
				'max_score': 1,
				'order': 1,
			},
			format='json',
		)

		self.client.force_authenticate(user=self.learner_user)
		submit_response = self.client.post(
			f'/api/challenges/{challenge_id}/submit/',
			{
				'answers': [
					{'question_id': question.data['id'], 'answer_text': 'YES'},
				],
			},
			format='json',
		)
		self.assertEqual(submit_response.status_code, status.HTTP_201_CREATED)

		profile = UserProfile.objects.get(user=self.learner_user)
		self.assertEqual(profile.current_streak, 1)
		self.assertEqual(profile.max_streak, 1)
		self.assertEqual(profile.last_activity_date, timezone.localdate())
		daily_activity = UserDailyActivity.objects.get(user=self.learner_user, activity_date=timezone.localdate())
		self.assertEqual(daily_activity.challenges_completed, 1)
		self.assertEqual(daily_activity.points_earned, 10)
		self.assertGreater(daily_activity.activity_score, 0)

	def test_challenge_completion_increments_streak_on_consecutive_day(self):
		profile = UserProfile.objects.get(user=self.learner_user)
		profile.current_streak = 3
		profile.last_activity_date = timezone.localdate() - timedelta(days=1)
		profile.save(update_fields=['current_streak', 'last_activity_date'])

		self.client.force_authenticate(user=self.admin_user)
		challenge_response = self.client.post(
			'/api/challenges/',
			{
				'title': 'Streak Increment Challenge',
				'description': 'Consecutive day',
				'difficulty': 'easy',
				'points': 10,
				'time_limit_minutes': 10,
				'lesson': self.lesson.id,
			},
			format='json',
		)
		challenge_id = challenge_response.data['id']
		question = self.client.post(
			f'/api/challenges/{challenge_id}/questions/',
			{
				'question_text': 'Type YES',
				'question_type': 'short_text_strict',
				'correct_answer': 'YES',
				'max_score': 1,
				'order': 1,
			},
			format='json',
		)

		self.client.force_authenticate(user=self.learner_user)
		submit_response = self.client.post(
			f'/api/challenges/{challenge_id}/submit/',
			{
				'answers': [
					{'question_id': question.data['id'], 'answer_text': 'YES'},
				],
			},
			format='json',
		)
		self.assertEqual(submit_response.status_code, status.HTTP_201_CREATED)

		profile.refresh_from_db()
		self.assertEqual(profile.current_streak, 4)
		self.assertEqual(profile.max_streak, 4)
		self.assertEqual(profile.last_activity_date, timezone.localdate())

	def test_challenge_completion_resets_streak_after_gap(self):
		profile = UserProfile.objects.get(user=self.learner_user)
		profile.current_streak = 6
		profile.last_activity_date = timezone.localdate() - timedelta(days=3)
		profile.save(update_fields=['current_streak', 'last_activity_date'])

		self.client.force_authenticate(user=self.admin_user)
		challenge_response = self.client.post(
			'/api/challenges/',
			{
				'title': 'Streak Reset Challenge',
				'description': 'Gap reset',
				'difficulty': 'easy',
				'points': 10,
				'time_limit_minutes': 10,
				'lesson': self.lesson.id,
			},
			format='json',
		)
		challenge_id = challenge_response.data['id']
		question = self.client.post(
			f'/api/challenges/{challenge_id}/questions/',
			{
				'question_text': 'Type YES',
				'question_type': 'short_text_strict',
				'correct_answer': 'YES',
				'max_score': 1,
				'order': 1,
			},
			format='json',
		)

		self.client.force_authenticate(user=self.learner_user)
		submit_response = self.client.post(
			f'/api/challenges/{challenge_id}/submit/',
			{
				'answers': [
					{'question_id': question.data['id'], 'answer_text': 'YES'},
				],
			},
			format='json',
		)
		self.assertEqual(submit_response.status_code, status.HTTP_201_CREATED)

		profile.refresh_from_db()
		self.assertEqual(profile.current_streak, 1)
		self.assertEqual(profile.max_streak, 6)
		self.assertEqual(profile.last_activity_date, timezone.localdate())
