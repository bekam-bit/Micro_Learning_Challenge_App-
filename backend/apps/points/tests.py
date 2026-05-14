from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from apps.categories.models import Category
from apps.challenges.models import Challenge, ChallengeAttempt, ChallengeQuestion
from apps.lessons.models import Lesson
from apps.users.models import UserProfile

from .models import PointTransaction
from .services import upsert_point_transaction


class PointTransactionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='points_user',
            email='points_user@example.com',
            password='Password123!',
        )

    def test_upsert_point_transaction_is_idempotent_per_source(self):
        upsert_point_transaction(
            user=self.user,
            points=10,
            source_type=PointTransaction.SOURCE_CHALLENGE_ATTEMPT,
            source_id=101,
            reason='Initial',
        )
        upsert_point_transaction(
            user=self.user,
            points=15,
            source_type=PointTransaction.SOURCE_CHALLENGE_ATTEMPT,
            source_id=101,
            reason='Updated',
        )

        self.assertEqual(PointTransaction.objects.filter(user=self.user).count(), 1)
        tx = PointTransaction.objects.get(user=self.user)
        self.assertEqual(tx.points, 15)

        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.total_points, 15)

    def test_challenge_attempt_progress_publishes_points_transaction(self):
        category = Category.objects.create(name='Points Cat', description='desc')
        lesson = Lesson.objects.create(
            title='Points Lesson',
            content='Lesson content',
            video_url='https://example.com/video',
            category=category,
            order=1,
        )
        challenge = Challenge.objects.create(
            title='Points Challenge',
            description='desc',
            difficulty='easy',
            points=20,
            lesson=lesson,
        )
        ChallengeQuestion.objects.create(
            challenge=challenge,
            question_text='2+2',
            correct_answer='4',
            max_score=1,
            order=1,
        )
        attempt = ChallengeAttempt.objects.create(
            challenge=challenge,
            user=self.user,
            is_submitted=True,
            points_awarded=12,
        )

        attempt.update_user_progress()

        tx = PointTransaction.objects.get(
            user=self.user,
            source_type=PointTransaction.SOURCE_CHALLENGE_ATTEMPT,
            source_id=attempt.id,
        )
        self.assertEqual(tx.points, 12)

        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.total_points, 12)


class AdminPointTransactionApiTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(
            username='points_admin',
            email='points_admin@example.com',
            password='Password123!',
            role='admin',
        )
        self.learner = User.objects.create_user(
            username='points_learner',
            email='points_learner@example.com',
            password='Password123!',
            role='learner',
        )

    def test_admin_can_list_point_transactions(self):
        upsert_point_transaction(
            user=self.learner,
            points=18,
            source_type=PointTransaction.SOURCE_CHALLENGE_ATTEMPT,
            source_id=9001,
            reason='Challenge reward',
        )
        self.client.force_authenticate(user=self.admin)

        response = self.client.get('/api/points/admin/transactions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['points'], 18)
        self.assertEqual(response.data['results'][0]['username'], 'points_learner')

    def test_non_admin_cannot_list_point_transactions(self):
        self.client.force_authenticate(user=self.learner)
        response = self.client.get('/api/points/admin/transactions/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
