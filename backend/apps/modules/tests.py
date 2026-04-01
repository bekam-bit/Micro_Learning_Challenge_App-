from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from apps.categories.models import Category

from .models import Module

User = get_user_model()
class ModuleAPITests(APITestCase):
	def test_public_module_detail_hides_inactive_category_module(self):
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

	def test_public_module_list_hides_inactive_category_modules(self):
		response = self.client.get('/api/modules/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		titles = [item['title'] for item in response.data['results']]
		self.assertIn(self.active_module.title, titles)
		self.assertNotIn(self.hidden_module.title, titles)

	def test_module_list_filters_by_category_id(self):
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
