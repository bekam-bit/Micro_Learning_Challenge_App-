from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0009_challenge_challenge_diff_ct_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='is_daily',
            field=models.BooleanField(default=False),
        ),
        migrations.RemoveConstraint(
            model_name='challenge',
            name='challenge_exactly_one_owner',
        ),
        migrations.AddConstraint(
            model_name='challenge',
            constraint=models.CheckConstraint(
                condition=(
                    (
                        Q(is_daily=False)
                        & (
                            Q(lesson__isnull=False, module__isnull=True, category__isnull=True)
                            | Q(lesson__isnull=True, module__isnull=False, category__isnull=True)
                            | Q(lesson__isnull=True, module__isnull=True, category__isnull=False)
                        )
                    )
                    | Q(is_daily=True, lesson__isnull=True, module__isnull=True, category__isnull=True)
                ),
                name='challenge_owner_rule_with_daily',
            ),
        ),
        migrations.AddIndex(
            model_name='challenge',
            index=models.Index(fields=['is_daily', 'created_at'], name='challenge_daily_ct_idx'),
        ),
    ]
