from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import UserDailyActivity, UserProfile


TEST_LEARNER_USERNAME = "bekiyo1234"
TEST_LEARNER_EMAIL = "bekiyo@gmail.com"
TEST_LEARNER_PASSWORD = "beki@1234"

TEST_ADMIN_USERNAME = "admin_user"
TEST_ADMIN_EMAIL = "admin_user@example.com"
TEST_ADMIN_PASSWORD = "StrongPass123"


class UserProfileSignalTests(TestCase):
	def test_profile_is_auto_created_when_user_is_created(self):
		user_model = get_user_model()
		user = user_model.objects.create_user(
			username=TEST_LEARNER_USERNAME,
			email=TEST_LEARNER_EMAIL,
			password=TEST_LEARNER_PASSWORD,
		)

		self.assertTrue(UserProfile.objects.filter(user=user).exists())

	def test_admin_role_sets_is_staff_true(self):
		user_model = get_user_model()
		user = user_model.objects.create_user(
			username="admin_role_user",
			email="admin_role_user@example.com",
			password="StrongPass123",
			role="admin",
		)

		self.assertTrue(user.is_staff)

	def test_learner_role_sets_is_staff_false(self):
		user_model = get_user_model()
		user = user_model.objects.create_user(
			username="learner_role_user",
			email="learner_role_user@example.com",
			password="StrongPass123",
			role="learner",
		)

		self.assertFalse(user.is_staff)


class AuthApiTests(APITestCase):
	def test_register_creates_user_and_profile(self):
		payload = {
			"username": TEST_LEARNER_USERNAME,
			"email": TEST_LEARNER_EMAIL,
			"password": TEST_LEARNER_PASSWORD,
		}

		response = self.client.post(reverse("register"), payload, format="json")

		self.assertEqual(response.status_code, status.HTTP_201_CREATED)
		user_model = get_user_model()
		user = user_model.objects.get(username=payload["username"])
		self.assertTrue(UserProfile.objects.filter(user=user).exists())

	def test_logout_blacklists_refresh_token(self):
		user_model = get_user_model()
		user_model.objects.create_user(
			username=TEST_LEARNER_USERNAME,
			email=TEST_LEARNER_EMAIL,
			password=TEST_LEARNER_PASSWORD,
		)

		login_response = self.client.post(
			reverse("login"),
			{"username": TEST_LEARNER_USERNAME, "password": TEST_LEARNER_PASSWORD},
			format="json",
		)

		self.assertEqual(login_response.status_code, status.HTTP_200_OK)
		access = login_response.data["access"]
		refresh = login_response.data["refresh"]

		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
		logout_response = self.client.post(
			reverse("logout"),
			{"refresh": refresh},
			format="json",
		)

		self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

		refresh_response = self.client.post(
			reverse("token_refresh"),
			{"refresh": refresh},
			format="json",
		)
		self.assertIn(
			refresh_response.status_code,
			(status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED),
		)

	def test_profile_contains_knowledge_momentum(self):
		user_model = get_user_model()
		user = user_model.objects.create_user(
			username=TEST_LEARNER_USERNAME,
			email=TEST_LEARNER_EMAIL,
			password=TEST_LEARNER_PASSWORD,
		)
		UserDailyActivity.objects.create(
			user=user,
			activity_date=user.date_joined.date(),
			activity_score=35,
		)

		login_response = self.client.post(
			reverse("login"),
			{"username": TEST_LEARNER_USERNAME, "password": TEST_LEARNER_PASSWORD},
			format="json",
		)
		self.assertEqual(login_response.status_code, status.HTTP_200_OK)

		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
		me_response = self.client.get(reverse("profile"), format="json")

		self.assertEqual(me_response.status_code, status.HTTP_200_OK)
		self.assertIn("knowledge_momentum", me_response.data)
		self.assertIn("days", me_response.data["knowledge_momentum"])

	def test_non_admin_cannot_list_users(self):
		user_model = get_user_model()
		user_model.objects.create_user(
			username="learner_user",
			email="learner_user@example.com",
			password="StrongPass123",
		)

		login_response = self.client.post(
			reverse("login"),
			{"username": "learner_user", "password": "StrongPass123"},
			format="json",
		)
		self.assertEqual(login_response.status_code, status.HTTP_200_OK)

		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
		response = self.client.get(reverse("user_list"), format="json")
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

	def test_admin_can_list_users_and_update_user_role(self):
		user_model = get_user_model()
		admin_user = user_model.objects.create_user(
			username=TEST_ADMIN_USERNAME,
			email=TEST_ADMIN_EMAIL,
			password=TEST_ADMIN_PASSWORD,
			role="admin",
		)
		target_user = user_model.objects.create_user(
			username="target_user",
			email="target_user@example.com",
			password="StrongPass123",
		)

		login_response = self.client.post(
			reverse("login"),
			{"username": admin_user.username, "password": TEST_ADMIN_PASSWORD},
			format="json",
		)
		self.assertEqual(login_response.status_code, status.HTTP_200_OK)

		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")

		list_response = self.client.get(reverse("user_list"), format="json")
		self.assertEqual(list_response.status_code, status.HTTP_200_OK)

		update_response = self.client.patch(
			reverse("user_role_update", kwargs={"pk": target_user.id}),
			{"role": "admin"},
			format="json",
		)
		self.assertEqual(update_response.status_code, status.HTTP_200_OK)

		target_user.refresh_from_db()
		self.assertEqual(target_user.role, "admin")
		self.assertTrue(target_user.is_staff)

	def test_learner_cannot_self_promote_from_profile_endpoint(self):
		user_model = get_user_model()
		user_model.objects.create_user(
			username="self_promote_user",
			email="self_promote_user@example.com",
			password="StrongPass123",
			role="learner",
		)

		login_response = self.client.post(
			reverse("login"),
			{"username": "self_promote_user", "password": "StrongPass123"},
			format="json",
		)
		self.assertEqual(login_response.status_code, status.HTTP_200_OK)

		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
		patch_response = self.client.patch(
			reverse("profile"),
			{"role": "admin"},
			format="json",
		)
		self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

		user = user_model.objects.get(username="self_promote_user")
		self.assertEqual(user.role, "learner")
		self.assertFalse(user.is_staff)

	def test_cannot_demote_last_active_admin(self):
		user_model = get_user_model()
		admin_user = user_model.objects.create_user(
			username="single_admin",
			email="single_admin@example.com",
			password=TEST_ADMIN_PASSWORD,
			role="admin",
		)

		login_response = self.client.post(
			reverse("login"),
			{"username": admin_user.username, "password": TEST_ADMIN_PASSWORD},
			format="json",
		)
		self.assertEqual(login_response.status_code, status.HTTP_200_OK)

		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
		update_response = self.client.patch(
			reverse("user_role_update", kwargs={"pk": admin_user.id}),
			{"role": "learner"},
			format="json",
		)

		self.assertEqual(update_response.status_code, status.HTTP_400_BAD_REQUEST)
		admin_user.refresh_from_db()
		self.assertEqual(admin_user.role, "admin")
