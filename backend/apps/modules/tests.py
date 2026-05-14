from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.categories.models import Category
from apps.progress.models import UserProgress

from .models import Module, ModuleEnrollment

User = get_user_model()
class ModuleAPITests(APITestCase):
	def test_authenticated_module_detail_hides_inactive_category_module(self):
		self.client.force_authenticate(user=self.learner_user)
		# Should return 404 for module in inactive category
		response = self.client.get(f'/api/modules/{self.hidden_module.id}/')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def setUp(self):
		self.active_category = Category.objects.create(
			name='Data Analytics',
			slug='data-analytics',
			description='Active category',
			icon='chart',
			display_order=1,
			is_active=True,
		)
		self.inactive_category = Category.objects.create(
			name='Deprecated',
			slug='deprecated',
			description='Inactive category',
			icon='archive',
			display_order=2,
			is_active=False,
		)
		self.active_module = Module.objects.create(
			category=self.active_category,
			title='SQL Basics',
			description='Learn SQL',
		)
		self.hidden_module = Module.objects.create(
			category=self.inactive_category,
			title='Old Tech',
			description='Legacy content',
		)
		self.admin_user = User.objects.create_user(
			username='admin_modules',
			email='admin_modules@example.com',
			password='StrongPass123!',
			role=User.ROLE_ADMIN,
		)
		self.learner_user = User.objects.create_user(
			username='learner_modules',
			email='learner_modules@example.com',
			password='StrongPass123!',
			role=User.ROLE_LEARNER,
		)

	def test_authenticated_module_list_hides_inactive_category_modules(self):
		self.client.force_authenticate(user=self.learner_user)
		response = self.client.get('/api/modules/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		titles = [item['title'] for item in response.data['results']]
		self.assertIn(self.active_module.title, titles)
		self.assertNotIn(self.hidden_module.title, titles)

	def test_module_list_filters_by_category_id(self):
		self.client.force_authenticate(user=self.learner_user)
		response = self.client.get(f'/api/modules/?category_id={self.active_category.id}')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		results = response.data['results']
		self.assertEqual(len(results), 1)
		self.assertEqual(results[0]['title'], 'SQL Basics')

	def test_module_list_supports_search_and_sort(self):
		Module.objects.create(
			category=self.active_category,
			title='API Design',
			description='Design APIs',
		)
		self.client.force_authenticate(user=self.learner_user)
		response = self.client.get('/api/modules/?search=api&sort_by=-title')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		results = response.data['results']
		self.assertEqual(len(results), 1)
		self.assertEqual(results[0]['title'], 'API Design')

	def test_admin_can_create_module_and_assign_category(self):
		self.client.force_authenticate(user=self.admin_user)
		payload = {
			'category': self.active_category.id,
			'title': 'Python Foundations',
			'description': 'Python intro module',
		}
		response = self.client.post('/api/modules/', payload, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertTrue(Module.objects.filter(title='Python Foundations', category=self.active_category).exists())

	def test_authenticated_module_list_returns_enroll_action_for_active_module(self):
		self.client.force_authenticate(user=self.learner_user)
		response = self.client.get('/api/modules/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		first = next(item for item in response.data['results'] if item['id'] == self.active_module.id)
		self.assertEqual(first['module_action'], 'enroll')

	def test_module_list_returns_coming_soon_action(self):
		coming_soon_module = Module.objects.create(
			category=self.active_category,
			title='WebGL Mastery',
			description='Soon',
			status='coming_soon',
		)
		self.client.force_authenticate(user=self.learner_user)
		response = self.client.get('/api/modules/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		item = next(result for result in response.data['results'] if result['id'] == coming_soon_module.id)
		self.assertEqual(item['module_action'], 'coming_soon')

	def test_authenticated_user_gets_enroll_action_without_enrollment(self):
		learner = User.objects.create_user(
			username='learner_start',
			email='learner_start@example.com',
			password='StrongPass123!',
			role=User.ROLE_LEARNER,
		)
		self.client.force_authenticate(user=learner)
		response = self.client.get('/api/modules/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		item = next(result for result in response.data['results'] if result['id'] == self.active_module.id)
		self.assertEqual(item['module_action'], 'enroll')
		self.assertEqual(item['module_progress_percent'], 0)
		self.assertEqual(item['module_completed_parts'], 0)
		self.assertEqual(item['module_total_parts'], 0)

	def test_authenticated_enrolled_user_gets_start_action_without_progress(self):
		learner = User.objects.create_user(
			username='learner_enrolled',
			email='learner_enrolled@example.com',
			password='StrongPass123!',
			role=User.ROLE_LEARNER,
		)
		ModuleEnrollment.objects.create(user=learner, module=self.active_module)
		self.client.force_authenticate(user=learner)
		response = self.client.get('/api/modules/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		item = next(result for result in response.data['results'] if result['id'] == self.active_module.id)
		self.assertEqual(item['module_action'], 'start')

	def test_authenticated_user_gets_resume_action_with_progress(self):
		learner = User.objects.create_user(
			username='learner_resume',
			email='learner_resume@example.com',
			password='StrongPass123!',
			role=User.ROLE_LEARNER,
		)
		ModuleEnrollment.objects.create(user=learner, module=self.active_module)
		UserProgress.objects.create(
			user=learner,
			module=self.active_module,
			completed=False,
			completed_parts=1,
			total_parts=3,
			progress_percent=33,
		)
		self.client.force_authenticate(user=learner)
		response = self.client.get('/api/modules/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		item = next(result for result in response.data['results'] if result['id'] == self.active_module.id)
		self.assertEqual(item['module_action'], 'resume')
		self.assertEqual(item['module_progress_percent'], 33)
		self.assertEqual(item['module_completed_parts'], 1)
		self.assertEqual(item['module_total_parts'], 3)

	def test_module_detail_includes_module_learning_fields(self):
		learner = User.objects.create_user(
			username='learner_detail',
			email='learner_detail@example.com',
			password='StrongPass123!',
			role=User.ROLE_LEARNER,
		)
		ModuleEnrollment.objects.create(user=learner, module=self.active_module)
		UserProgress.objects.create(
			user=learner,
			module=self.active_module,
			completed=False,
			completed_parts=2,
			total_parts=5,
			progress_percent=40,
		)
		self.client.force_authenticate(user=learner)
		response = self.client.get(f'/api/modules/{self.active_module.id}/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['module_action'], 'resume')
		self.assertEqual(response.data['module_progress_percent'], 40)
		self.assertEqual(response.data['module_completed_parts'], 2)
		self.assertEqual(response.data['module_total_parts'], 5)

	def test_authenticated_user_can_enroll_module(self):
		learner = User.objects.create_user(
			username='learner_enroll_api',
			email='learner_enroll_api@example.com',
			password='StrongPass123!',
			role=User.ROLE_LEARNER,
		)
		self.client.force_authenticate(user=learner)
		response = self.client.post(f'/api/modules/{self.active_module.id}/enroll/')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertTrue(ModuleEnrollment.objects.filter(user=learner, module=self.active_module).exists())

		module_list_response = self.client.get('/api/modules/')
		self.assertEqual(module_list_response.status_code, status.HTTP_200_OK)
		item = next(result for result in module_list_response.data['results'] if result['id'] == self.active_module.id)
		self.assertEqual(item['module_action'], 'start')

	def test_enroll_endpoint_is_idempotent(self):
		learner = User.objects.create_user(
			username='learner_enroll_repeat',
			email='learner_enroll_repeat@example.com',
			password='StrongPass123!',
			role=User.ROLE_LEARNER,
		)
		self.client.force_authenticate(user=learner)
		first = self.client.post(f'/api/modules/{self.active_module.id}/enroll/')
		second = self.client.post(f'/api/modules/{self.active_module.id}/enroll/')
		self.assertEqual(first.status_code, status.HTTP_201_CREATED)
		self.assertEqual(second.status_code, status.HTTP_200_OK)
		self.assertEqual(ModuleEnrollment.objects.filter(user=learner, module=self.active_module).count(), 1)
