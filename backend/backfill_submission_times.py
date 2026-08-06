"""
Backfill submitted_at for old challenge attempts that don't have it set.
Run this once to fix old data.

Usage:
  python manage.py shell < backfill_submission_times.py
"""

from django.utils import timezone
from apps.challenges.models import ChallengeAttempt

# Find all submitted attempts without submitted_at
attempts = ChallengeAttempt.objects.filter(
    is_submitted=True,
    submitted_at__isnull=True
)

count = attempts.count()
print(f"Found {count} attempts without submitted_at")

if count > 0:
    for attempt in attempts:
        # Use last_saved_at as approximate submission time
        attempt.submitted_at = attempt.last_saved_at
        print(f"  - Attempt #{attempt.id}: Set submitted_at to {attempt.last_saved_at}")
    
    # Bulk update
    ChallengeAttempt.objects.bulk_update(attempts, ['submitted_at'])
    print(f"\n✅ Successfully updated {count} attempts")
else:
    print("✅ No attempts need updating")
