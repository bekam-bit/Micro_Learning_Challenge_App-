from django.db.models import Sum

from apps.users.models import UserProfile

from .models import PointTransaction


def sync_user_total_points(user):
    total = PointTransaction.objects.filter(user=user).aggregate(total=Sum('points'))['total'] or 0
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.total_points = total
    profile.save(update_fields=['total_points'])
    return total


def upsert_point_transaction(*, user, points, source_type, source_id, reason='', metadata=None):
    transaction, _ = PointTransaction.objects.update_or_create(
        user=user,
        source_type=source_type,
        source_id=source_id,
        defaults={
            'points': points,
            'reason': reason,
            'metadata': metadata or {},
        },
    )
    return transaction
