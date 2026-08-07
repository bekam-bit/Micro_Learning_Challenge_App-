"""
Check if ChallengeAttempt records have started_at and submitted_at set.
Run this to diagnose the time tracking issue.

Usage:
  python manage.py shell < check_attempt_times.py
"""

from apps.challenges.models import ChallengeAttempt
from django.db.models import Q

# Get all submitted attempts
attempts = ChallengeAttempt.objects.filter(is_submitted=True).order_by('-submitted_at')[:10]

print(f"\n{'='*80}")
print(f"Checking last 10 submitted attempts:")
print(f"{'='*80}\n")

for attempt in attempts:
    print(f"Attempt #{attempt.id} (Challenge: {attempt.challenge.title})")
    print(f"  User: {attempt.user.username}")
    print(f"  started_at: {attempt.started_at}")
    print(f"  submitted_at: {attempt.submitted_at}")
    print(f"  is_submitted: {attempt.is_submitted}")
    
    if attempt.started_at and attempt.submitted_at:
        delta = attempt.submitted_at - attempt.started_at
        seconds = int(delta.total_seconds())
        print(f"  ✅ Time taken: {seconds} seconds")
    else:
        print(f"  ❌ Missing time data!")
        if not attempt.started_at:
            print(f"     - started_at is None")
        if not attempt.submitted_at:
            print(f"     - submitted_at is None")
    print()

# Check how many have missing data
total = ChallengeAttempt.objects.filter(is_submitted=True).count()
missing_started = ChallengeAttempt.objects.filter(is_submitted=True, started_at__isnull=True).count()
missing_submitted = ChallengeAttempt.objects.filter(is_submitted=True, submitted_at__isnull=True).count()

print(f"\n{'='*80}")
print(f"Summary:")
print(f"{'='*80}")
print(f"Total submitted attempts: {total}")
print(f"Missing started_at: {missing_started}")
print(f"Missing submitted_at: {missing_submitted}")
print(f"With complete time data: {total - missing_started - missing_submitted}")
