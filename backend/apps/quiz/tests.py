from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.categories.models import Category
from apps.lessons.models import Lesson
from apps.modules.models import Module
from apps.progress.models import UserProgress

from .models.Answer import Answer
from .models.Question import Question
from .models.Quiz import Quiz
from .models.QuizSubmission import QuizSubmission


User = get_user_model()


class QuizSubmissionValidationTests(APITestCase):
	def setUp(self):
		self.learner = User.objects.create_user(
			username='quiz_learner',
			email='quiz_learner@example.com',
			password='StrongPass123!',
			role=User.ROLE_LEARNER,
		)
		self.client.force_authenticate(user=self.learner)
		self.category = Category.objects.create(name='Quiz Category', description='Category for quiz tests')
		self.module = Module.objects.create(
			category=self.category,
			title='Quiz Module',
			description='Module for quiz tests',
			status='active',
			level='beginner',
		)
		self.lesson = Lesson.objects.create(
			title='Quiz Lesson',
			content='Quiz lesson content',
			video_url='https://example.com/quiz-lesson.mp4',
			category=self.category,
			module=self.module,
			order=1,
		)
		self.other_lesson = Lesson.objects.create(
			title='Other Quiz Lesson',
			content='Other lesson content',
			video_url='https://example.com/other-lesson.mp4',
			category=self.category,
			module=self.module,
			order=2,
		)

		self.quiz = Quiz.objects.create(title='Quiz A', description='Main quiz', lesson=self.lesson)
		self.question_1 = Question.objects.create(
			quiz=self.quiz,
			prompt='2 + 2 = ?',
			question_type=Question.TYPE_SINGLE_CHOICE,
			order=1,
		)
		self.answer_1_correct = Answer.objects.create(
			question=self.question_1,
			text='4',
			explanation='4 is correct because adding two and two equals four.',
			is_correct=True,
			order=1,
		)
		self.answer_1_wrong = Answer.objects.create(
			question=self.question_1,
			text='5',
			explanation='5 is incorrect because it overcounts by one.',
			is_correct=False,
			order=2,
		)

		self.other_quiz = Quiz.objects.create(title='Quiz B', description='Other quiz', lesson=self.other_lesson)
		self.other_question = Question.objects.create(
			quiz=self.other_quiz,
			prompt='Other question',
			question_type=Question.TYPE_SINGLE_CHOICE,
			order=1,
		)

		self.question_2 = Question.objects.create(
			quiz=self.quiz,
			prompt='Select prime numbers',
			question_type=Question.TYPE_MULTIPLE_CHOICE,
			order=2,
		)
		self.answer_2_a = Answer.objects.create(
			question=self.question_2,
			text='2',
			explanation='2 is a prime number.',
			is_correct=True,
			order=1,
		)
		self.answer_2_b = Answer.objects.create(
			question=self.question_2,
			text='4',
			explanation='4 is not prime because it has divisors 1, 2, 4.',
			is_correct=False,
			order=2,
		)
		self.answer_2_c = Answer.objects.create(
			question=self.question_2,
			text='3',
			explanation='3 is a prime number.',
			is_correct=True,
			order=3,
		)
		self.other_answer = Answer.objects.create(
			question=self.other_question,
			text='Other',
			explanation='Other quiz explanation.',
			is_correct=True,
			order=1,
		)

		self.submit_url = f'/api/quiz/quizzes/{self.quiz.id}/submit/'

	def test_submit_quiz_scores_valid_answers(self):
		payload = {
			'answers': [
				{'question_id': self.question_1.id, 'answer_id': self.answer_1_correct.id},
			]
		}

		response = self.client.post(self.submit_url, payload, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['total_questions'], 2)
		self.assertEqual(response.data['correct_answers'], 1)
		self.assertEqual(response.data['score'], 50)
		self.assertIn('results', response.data)
		self.assertEqual(response.data['results'][0]['question_id'], self.question_1.id)
		self.assertTrue(response.data['results'][0]['is_correct'])
		self.assertEqual(response.data['results'][0]['selected_answer']['id'], self.answer_1_correct.id)
		self.assertEqual(response.data['results'][0]['correct_answers'][0]['id'], self.answer_1_correct.id)
		self.assertEqual(
			response.data['results'][0]['selected_answer']['explanation'],
			'4 is correct because adding two and two equals four.',
		)
		self.assertIn('explanation', response.data['results'][0])
		self.assertEqual(
			response.data['results'][0]['explanation'],
			'4 is correct because adding two and two equals four.',
		)
		self.assertTrue(
			QuizSubmission.objects.filter(
				quiz=self.quiz,
				user=self.learner,
				is_submitted=True,
				correct_answers=1,
				total_questions=2,
				score=50,
			).exists()
		)

	def test_submit_quiz_updates_module_progress_with_quiz_completion(self):
		payload = {
			'answers': [
				{'question_id': self.question_1.id, 'answer_id': self.answer_1_correct.id},
			]
		}

		response = self.client.post(self.submit_url, payload, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		module_progress = UserProgress.objects.get(user=self.learner, module=self.module)
		self.assertEqual(module_progress.total_parts, 4)
		self.assertEqual(module_progress.completed_parts, 1)
		self.assertEqual(module_progress.progress_percent, 25)

	def test_submit_quiz_returns_explanation_for_incorrect_answer(self):
		payload = {
			'answers': [
				{'question_id': self.question_1.id, 'answer_id': self.answer_1_wrong.id},
			]
		}

		response = self.client.post(self.submit_url, payload, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertFalse(response.data['results'][0]['is_correct'])
		self.assertEqual(response.data['results'][0]['explanation'], '5 is incorrect because it overcounts by one.')

	def test_submit_quiz_rejects_question_from_other_quiz(self):
		payload = {
			'answers': [
				{'question_id': self.other_question.id, 'answer_id': self.other_answer.id},
			]
		}

		response = self.client.post(self.submit_url, payload, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('does not belong to quiz', response.data['detail'])

	def test_submit_quiz_rejects_answer_not_matching_question(self):
		payload = {
			'answers': [
				{'question_id': self.question_1.id, 'answer_id': self.other_answer.id},
			]
		}

		response = self.client.post(self.submit_url, payload, format='json')
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('is invalid for question', response.data['detail'])

	def test_user_quiz_view_hides_answer_keys(self):
		response = self.client.get(f'/api/quiz/quizzes/{self.quiz.id}/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['lesson'], self.lesson.id)
		answers = response.data['questions'][0]['answers']
		self.assertGreaterEqual(len(answers), 1)
		self.assertNotIn('is_correct', answers[0])
		self.assertIn('question_type', response.data['questions'][0])
		self.assertIn('answer_format', response.data['questions'][0])

	def test_user_quiz_list_endpoint_exists(self):
		response = self.client.get('/api/quiz/quizzes/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertGreaterEqual(len(response.data), 2)

	def test_user_quiz_list_can_filter_by_lesson(self):
		response = self.client.get(f'/api/quiz/quizzes/?lesson_id={self.lesson.id}')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(len(response.data), 1)
		self.assertEqual(response.data[0]['lesson'], self.lesson.id)

	def test_submit_quiz_supports_multiple_choice_answer_ids(self):
		payload = {
			'answers': [
				{
					'question_id': self.question_2.id,
					'answer_ids': [self.answer_2_a.id, self.answer_2_c.id],
				},
			]
		}

		response = self.client.post(self.submit_url, payload, format='json')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertTrue(response.data['results'][0]['is_correct'])
		self.assertEqual(response.data['results'][0]['question_type'], 'multiple_choice')
		self.assertEqual(len(response.data['results'][0]['selected_answers']), 2)


class QuizAdminCrudTests(APITestCase):
	def setUp(self):
		self.admin_user = User.objects.create_user(
			username='quiz_admin',
			email='quiz_admin@example.com',
			password='StrongPass123!',
			role=User.ROLE_ADMIN,
		)
		self.client.force_authenticate(user=self.admin_user)

	def test_admin_can_crud_question_and_answer(self):
		category = Category.objects.create(name='Admin Quiz Category', description='Admin category')
		module = Module.objects.create(
			category=category,
			title='Admin Quiz Module',
			description='Admin module',
			status='active',
			level='beginner',
		)
		lesson = Lesson.objects.create(
			title='Admin Quiz Lesson',
			content='Admin lesson content',
			video_url='https://example.com/admin-lesson.mp4',
			category=category,
			module=module,
			order=1,
		)

		quiz_response = self.client.post(
			'/api/quiz/admin/quizzes/',
			{'lesson': lesson.id, 'title': 'Admin Quiz', 'description': 'CRUD test'},
			format='json',
		)
		self.assertEqual(quiz_response.status_code, status.HTTP_201_CREATED)
		quiz_id = quiz_response.data['id']
		self.assertEqual(quiz_response.data['lesson'], lesson.id)

		question_response = self.client.post(
			'/api/quiz/admin/questions/',
			{'quiz': quiz_id, 'prompt': 'Admin question?', 'question_type': 'single_choice', 'order': 1},
			format='json',
		)
		self.assertEqual(question_response.status_code, status.HTTP_201_CREATED)
		question_id = question_response.data['id']
		self.assertEqual(question_response.data['question_type'], 'single_choice')

		answer_response = self.client.post(
			'/api/quiz/admin/answers/',
			{
				'question': question_id,
				'text': 'Correct',
				'explanation': 'This is correct because it matches the expected concept.',
				'is_correct': True,
				'order': 1,
			},
			format='json',
		)
		self.assertEqual(answer_response.status_code, status.HTTP_201_CREATED)
		answer_id = answer_response.data['id']
		self.assertEqual(
			answer_response.data['explanation'],
			'This is correct because it matches the expected concept.',
		)

		patch_response = self.client.patch(
			f'/api/quiz/admin/answers/{answer_id}/',
			{'text': 'Updated Correct'},
			format='json',
		)
		self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
		self.assertEqual(patch_response.data['text'], 'Updated Correct')

		delete_response = self.client.delete(f'/api/quiz/admin/answers/{answer_id}/')
		self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
