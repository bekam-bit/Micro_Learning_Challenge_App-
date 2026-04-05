
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.categories.models import Category
from apps.modules.models import Module
from apps.lessons.models import Lesson
from django.contrib.auth import get_user_model

User = get_user_model()

class LessonAPITestCase(APITestCase):
	def setUp(self):
		self.admin = User.objects.create_user(
			username='admin',
			email='admin_lessons@example.com',
			password='adminpass',
			role='admin',
		)
		self.user = User.objects.create_user(
			username='user',
			email='user_lessons@example.com',
			password='userpass',
			role='learner',
		)
		self.category = Category.objects.create(name='Science', description='desc')
		self.module = Module.objects.create(category=self.category, title='Quantum', description='desc', status='active', level='beginner')
		self.lesson = Lesson.objects.create(
			title='Superposition',
			content='<p>Quantum superposition...</p>',
			video_url='https://example.com/video.mp4',
			category=self.category,
			module=self.module,
			order=1
		)
		self.list_url = reverse('lesson_list_create')
		self.detail_url = reverse('lesson_detail', args=[self.lesson.id])

	def test_lesson_list_pagination(self):
		self.client.force_authenticate(user=self.user)
		response = self.client.get(self.list_url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn('results', response.data)
		self.assertGreaterEqual(len(response.data['results']), 1)

	def test_lesson_detail_access_active_module(self):
		self.client.force_authenticate(user=self.user)
		response = self.client.get(self.detail_url)
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['id'], self.lesson.id)

	def test_lesson_create_requires_auth(self):
		data = {
			'title': 'Entanglement',
			'content': '<p>Quantum entanglement...</p>',
			'video_url': 'https://example.com/entangle.mp4',
			'category': self.category.id,
			'module': self.module.id,
			'order': 2
		}
		response = self.client.post(self.list_url, data)
		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_lesson_create_admin(self):
		self.client.force_authenticate(user=self.admin)
		data = {
			'title': 'Entanglement',
			'content': '<p>Quantum entanglement...</p>',
			'video_url': 'https://example.com/entangle.mp4',
			'category': self.category.id,
			'module': self.module.id,
			'order': 2
		}
		response = self.client.post(self.list_url, data)
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)

	def test_lesson_create_requires_video(self):
		self.client.force_authenticate(user=self.admin)
		data = {
			'title': 'No Video',
			'content': 'Missing video',
			'category': self.category.id,
			'module': self.module.id,
			'order': 3
		}
		response = self.client.post(self.list_url, data)
		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('non_field_errors', response.data)
