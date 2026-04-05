from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class SecurityRegressionTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='security_admin',
            email='security_admin@example.com',
            password='StrongPass123!',
            role=User.ROLE_ADMIN,
        )
        self.learner = User.objects.create_user(
            username='security_learner',
            email='security_learner@example.com',
            password='StrongPass123!',
            role=User.ROLE_LEARNER,
        )

    def _login_and_get_access(self, username, password):
        response = self.client.post(
            '/api/auth/login/',
            {'username': username, 'password': password},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return response.data['access']

    def test_auth_required_on_notifications_endpoint(self):
        response = self.client.get('/api/notifications/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_learner_cannot_access_admin_points_transactions(self):
        learner_token = self._login_and_get_access('security_learner', 'StrongPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {learner_token}')

        response = self.client.get('/api/points/admin/transactions/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_learner_cannot_access_admin_user_list(self):
        learner_token = self._login_and_get_access('security_learner', 'StrongPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {learner_token}')

        response = self.client.get('/api/auth/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_access_admin_routes(self):
        admin_token = self._login_and_get_access('security_admin', 'StrongPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {admin_token}')

        users_response = self.client.get('/api/auth/users/')
        points_response = self.client.get('/api/points/admin/transactions/')

        self.assertEqual(users_response.status_code, status.HTTP_200_OK)
        self.assertEqual(points_response.status_code, status.HTTP_200_OK)
