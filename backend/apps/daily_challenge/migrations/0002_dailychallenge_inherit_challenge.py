# Generated manually to convert DailyChallenge into a Challenge subclass.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('daily_challenge', '0001_initial'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        'ALTER TABLE daily_challenge_dailychallenge DROP CONSTRAINT daily_challenge_dailychallenge_pkey;'
                        'ALTER TABLE daily_challenge_dailychallenge DROP COLUMN id;'
                        'ALTER TABLE daily_challenge_dailychallenge RENAME COLUMN challenge_id TO challenge_ptr_id;'
                        'ALTER TABLE daily_challenge_dailychallenge '
                        'ADD CONSTRAINT daily_challenge_dailychallenge_pkey PRIMARY KEY (challenge_ptr_id);'
                    ),
                    reverse_sql=(
                        'ALTER TABLE daily_challenge_dailychallenge DROP CONSTRAINT daily_challenge_dailychallenge_pkey;'
                        'ALTER TABLE daily_challenge_dailychallenge RENAME COLUMN challenge_ptr_id TO challenge_id;'
                        'ALTER TABLE daily_challenge_dailychallenge ADD COLUMN id BIGSERIAL;'
                        'ALTER TABLE daily_challenge_dailychallenge '
                        'ADD CONSTRAINT daily_challenge_dailychallenge_pkey PRIMARY KEY (id);'
                    ),
                ),
            ],
            state_operations=[
                migrations.RenameField(
                    model_name='dailychallenge',
                    old_name='challenge',
                    new_name='challenge_ptr',
                ),
                migrations.RemoveField(
                    model_name='dailychallenge',
                    name='id',
                ),
                migrations.AlterField(
                    model_name='dailychallenge',
                    name='challenge_ptr',
                    field=models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to='challenges.challenge',
                    ),
                ),
                migrations.AlterModelOptions(
                    name='dailychallenge',
                    options={'ordering': ['-date', '-id']},
                ),
            ],
        ),
    ]
