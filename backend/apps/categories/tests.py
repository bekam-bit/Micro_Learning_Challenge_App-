from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category

User = get_user_model()


class CategoryAPITests(APITestCase):
	def setUp(self):
		self.active_category = Category.objects.create(
			name='Backend Systems',
			slug='backend-systems',
			description='Backend category',
			icon='database',
			display_order=2,
			is_active=True,
		)
		self.inactive_category = Category.objects.create(
			name='Legacy Systems',
			slug='legacy-systems',
			description='Legacy category',
			icon='archive',
			display_order=1,
			is_active=False,
		)
		self.admin_user = User.objects.create_user(
			username='admin_user',
			email='admin@example.com',
			password='StrongPass123!',
			role=User.ROLE_ADMIN,
		)

	def test_public_category_list_shows_only_active(self):
		response = self.client.get('/api/categories/')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		names = [item['name'] for item in response.data['results']]
		self.assertIn(self.active_category.name, names)
		self.assertNotIn(self.inactive_category.name, names)

	def test_public_category_detail_hides_inactive(self):
		response = self.client.get(f'/api/categories/{self.inactive_category.id}/')
		self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

	def test_category_list_search_and_sort(self):
		response = self.client.get('/api/categories/?search=backend&sort_by=name')
		self.assertEqual(response.status_code, status.HTTP_200_OK)
		results = response.data['results']
		self.assertEqual(len(results), 1)
		self.assertEqual(results[0]['name'], 'Backend Systems')

	def test_admin_can_create_category(self):
		self.client.force_authenticate(user=self.admin_user)
		payload = {
			'name': 'AI Foundations',
			'slug': 'ai-foundations',
			'description': 'AI category',
			'icon': 'brain',
			'display_order': 3,
			'is_active': True,
		}
		response = self.client.post('/api/categories/', payload, format='json')
		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		self.assertTrue(Category.objects.filter(slug='ai-foundations').exists())
