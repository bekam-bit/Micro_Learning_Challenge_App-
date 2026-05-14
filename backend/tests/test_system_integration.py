from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class FullSystemIntegrationTests(APITestCase):
    def setUp(self):
        self.admin_password = 'StrongPass123!'
        self.learner_password = 'StrongPass123!'

        self.admin_user = User.objects.create_user(
            username='integration_admin',
            email='integration_admin@example.com',
            password=self.admin_password,
            role=User.ROLE_ADMIN,
        )

        register_response = self.client.post(
            '/api/auth/register/',
            {
                'username': 'integration_learner',
                'email': 'integration_learner@example.com',
                'password': self.learner_password,
            },
            format='json',
        )
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        self.learner_user = User.objects.get(username='integration_learner')

        self.admin_access_token = self._login_and_get_access('integration_admin', self.admin_password)
        self.learner_access_token = self._login_and_get_access('integration_learner', self.learner_password)

    def _login_and_get_access(self, username, password):
        login_response = self.client.post(
            '/api/auth/login/',
            {
                'username': username,
                'password': password,
            },
            format='json',
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_response.data)
        return login_response.data['access']

    def _as_admin(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_access_token}')

    def _as_learner(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.learner_access_token}')

    def test_end_to_end_platform_integration_flow(self):
        # --- Admin creates base learning content ---
        self._as_admin()

        category_response = self.client.post(
            '/api/categories/',
            {
                'name': 'Integration Category',
                'slug': 'integration-category',
                'description': 'Integration test category',
                'icon': 'integration',
                'display_order': 1,
                'is_active': True,
            },
            format='json',
        )
        self.assertEqual(category_response.status_code, status.HTTP_201_CREATED)
        category_id = category_response.data['id']

        module_response = self.client.post(
            '/api/modules/',
            {
                'category': category_id,
                'title': 'Integration Module',
                'description': 'Integration module description',
                'status': 'active',
                'level': 'beginner',
                'estimated_time': 30,
            },
            format='json',
        )
        self.assertEqual(module_response.status_code, status.HTTP_201_CREATED)
        module_id = module_response.data['id']

        lesson_response = self.client.post(
            '/api/lessons/',
            {
                'title': 'Integration Lesson',
                'content': 'Integration lesson content',
                'video_url': 'https://example.com/integration-lesson',
                'order': 1,
                'category': category_id,
                'module': module_id,
            },
            format='json',
        )
        self.assertEqual(lesson_response.status_code, status.HTTP_201_CREATED)
        lesson_id = lesson_response.data['id']

        challenge_response = self.client.post(
            '/api/challenges/',
            {
                'title': 'Integration Challenge',
                'description': 'Challenge for integration testing',
                'difficulty': 'easy',
                'points': 20,
                'time_limit_minutes': 20,
                'lesson': lesson_id,
            },
            format='json',
        )
        self.assertEqual(challenge_response.status_code, status.HTTP_201_CREATED)
        challenge_id = challenge_response.data['id']

        question_response = self.client.post(
            f'/api/challenges/{challenge_id}/questions/',
            {
                'question_text': 'What is 2 + 2?',
                'correct_answer': '4',
                'max_score': 1,
                'order': 1,
            },
            format='json',
        )
        self.assertEqual(question_response.status_code, status.HTTP_201_CREATED)
        challenge_question_id = question_response.data['id']

        daily_response = self.client.post(
            '/api/daily-challenges/',
            {
                'date': str(timezone.localdate()),
                'title': 'Integration Daily Challenge',
                'description': 'Daily challenge for integration testing',
                'difficulty': 'easy',
                'points': 15,
                'time_limit_minutes': 15,
            },
            format='json',
        )
        self.assertEqual(daily_response.status_code, status.HTTP_201_CREATED)
        daily_challenge_id = daily_response.data['id']

        daily_question_response = self.client.post(
            f'/api/daily-challenges/{daily_challenge_id}/questions/',
            {
                'question_text': 'Type YES',
                'correct_answer': 'YES',
                'max_score': 1,
                'order': 1,
            },
            format='json',
        )
        self.assertEqual(daily_question_response.status_code, status.HTTP_201_CREATED)
        daily_question_id = daily_question_response.data['id']

        quiz_response = self.client.post(
            '/api/quiz/admin/quizzes/',
            {
                'lesson': lesson_id,
                'title': 'Integration Quiz',
                'description': 'Quiz for integration flow',
            },
            format='json',
        )
        self.assertEqual(quiz_response.status_code, status.HTTP_201_CREATED)
        quiz_id = quiz_response.data['id']

        quiz_question_response = self.client.post(
            '/api/quiz/admin/questions/',
            {
                'quiz': quiz_id,
                'prompt': 'Python is interpreted?',
                'question_type': 'single_choice',
                'order': 1,
            },
            format='json',
        )
        self.assertEqual(quiz_question_response.status_code, status.HTTP_201_CREATED)
        quiz_question_id = quiz_question_response.data['id']

        wrong_answer_response = self.client.post(
            '/api/quiz/admin/answers/',
            {
                'question': quiz_question_id,
                'text': 'No',
                'explanation': 'Python is interpreted.',
                'is_correct': False,
                'order': 1,
            },
            format='json',
        )
        self.assertEqual(wrong_answer_response.status_code, status.HTTP_201_CREATED)

        correct_answer_response = self.client.post(
            '/api/quiz/admin/answers/',
            {
                'question': quiz_question_id,
                'text': 'Yes',
                'explanation': 'Correct.',
                'is_correct': True,
                'order': 2,
            },
            format='json',
        )
        self.assertEqual(correct_answer_response.status_code, status.HTTP_201_CREATED)
        correct_answer_id = correct_answer_response.data['id']

        # --- Learner consumes and submits ---
        self._as_learner()

        profile_response = self.client.get('/api/auth/profile/')
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)

        self.assertEqual(self.client.get('/api/categories/').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get('/api/modules/').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get('/api/lessons/').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get('/api/challenges/').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get('/api/daily-challenges/').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get('/api/daily-challenges/today/').status_code, status.HTTP_200_OK)

        enroll_response = self.client.post(f'/api/modules/{module_id}/enroll/', {}, format='json')
        self.assertIn(enroll_response.status_code, {status.HTTP_200_OK, status.HTTP_201_CREATED})

        challenge_progress_response = self.client.post(
            f'/api/challenges/{challenge_id}/progress/',
            {
                'answers': [
                    {'question_id': challenge_question_id, 'answer_text': '4'},
                ]
            },
            format='json',
        )
        self.assertEqual(challenge_progress_response.status_code, status.HTTP_200_OK)

        challenge_submit_response = self.client.post(
            f'/api/challenges/{challenge_id}/submit/',
            {
                'answers': [
                    {'question_id': challenge_question_id, 'answer_text': '4'},
                ]
            },
            format='json',
        )
        self.assertEqual(challenge_submit_response.status_code, status.HTTP_201_CREATED)

        daily_submit_response = self.client.post(
            f'/api/daily-challenges/{daily_challenge_id}/submit/',
            {
                'answers': [
                    {'question_id': daily_question_id, 'answer_text': 'YES'},
                ]
            },
            format='json',
        )
        self.assertEqual(daily_submit_response.status_code, status.HTTP_201_CREATED)

        quizzes_list_response = self.client.get(f'/api/quiz/quizzes/?lesson_id={lesson_id}')
        self.assertEqual(quizzes_list_response.status_code, status.HTTP_200_OK)

        quiz_submit_response = self.client.post(
            f'/api/quiz/quizzes/{quiz_id}/submit/',
            {
                'answers': [
                    {'question_id': quiz_question_id, 'answer_id': correct_answer_id},
                ]
            },
            format='json',
        )
        self.assertEqual(quiz_submit_response.status_code, status.HTTP_200_OK)

        progress_list_response = self.client.get('/api/progress/')
        self.assertEqual(progress_list_response.status_code, status.HTTP_200_OK)

        progress_summary_response = self.client.get('/api/progress/summary/')
        self.assertEqual(progress_summary_response.status_code, status.HTTP_200_OK)

        notification_list_response = self.client.get('/api/notifications/')
        self.assertEqual(notification_list_response.status_code, status.HTTP_200_OK)
        self.assertIn('unread_count', notification_list_response.data)
        self.assertGreaterEqual(notification_list_response.data['count'], 1)

        first_notification_id = notification_list_response.data['results'][0]['id']
        mark_one_response = self.client.post(f'/api/notifications/{first_notification_id}/read/', {}, format='json')
        self.assertEqual(mark_one_response.status_code, status.HTTP_200_OK)

        mark_all_response = self.client.post('/api/notifications/read-all/', {}, format='json')
        self.assertEqual(mark_all_response.status_code, status.HTTP_200_OK)

        # --- Admin-only observability endpoints ---
        self._as_admin()

        admin_users_response = self.client.get('/api/auth/users/')
        self.assertEqual(admin_users_response.status_code, status.HTTP_200_OK)

        admin_progress_response = self.client.get('/api/progress/admin/')
        self.assertEqual(admin_progress_response.status_code, status.HTTP_200_OK)

        admin_points_response = self.client.get('/api/points/admin/transactions/')
        self.assertEqual(admin_points_response.status_code, status.HTTP_200_OK)
