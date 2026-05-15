# Generated manually to convert DailyChallenge into a Challenge subclass.

import django.db.models.deletion
from django.db import migrations, models
from django.conf import settings


def is_postgresql():
    """Check if the current database engine is PostgreSQL."""
    db_engine = settings.DATABASES.get('default', {}).get('ENGINE', '')
    return 'postgresql' in db_engine


def alter_for_postgresql(apps, schema_editor):
    """Alter table for PostgreSQL databases."""
    if not is_postgresql():
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            'ALTER TABLE daily_challenge_dailychallenge DROP CONSTRAINT daily_challenge_dailychallenge_pkey;'
        )
        cursor.execute(
            'ALTER TABLE daily_challenge_dailychallenge DROP COLUMN id;'
        )
        cursor.execute(
            'ALTER TABLE daily_challenge_dailychallenge RENAME COLUMN challenge_id TO challenge_ptr_id;'
        )
        cursor.execute(
            'ALTER TABLE daily_challenge_dailychallenge '
            'ADD CONSTRAINT daily_challenge_dailychallenge_pkey PRIMARY KEY (challenge_ptr_id);'
        )


def reverse_alter_for_postgresql(apps, schema_editor):
    """Reverse alter table for PostgreSQL databases."""
    if not is_postgresql():
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            'ALTER TABLE daily_challenge_dailychallenge DROP CONSTRAINT daily_challenge_dailychallenge_pkey;'
        )
        cursor.execute(
            'ALTER TABLE daily_challenge_dailychallenge RENAME COLUMN challenge_ptr_id TO challenge_id;'
        )
        cursor.execute(
            'ALTER TABLE daily_challenge_dailychallenge ADD COLUMN id BIGSERIAL;'
        )
        cursor.execute(
            'ALTER TABLE daily_challenge_dailychallenge '
            'ADD CONSTRAINT daily_challenge_dailychallenge_pkey PRIMARY KEY (id);'
        )


def migrate_sqlite_table(apps, schema_editor):
    """Migrate SQLite table by recreating it with the new schema."""
    if is_postgresql():
        return
    
    # For SQLite, we need to recreate the table
    # Get the old table data before deletion
    with schema_editor.connection.cursor() as cursor:
        # Drop the old table
        cursor.execute('DROP TABLE IF EXISTS daily_challenge_dailychallenge;')
        
        # Create the new table with the correct schema
        # The table should have challenge_ptr_id as primary key referencing challenges_challenge.id
        cursor.execute('''
            CREATE TABLE "daily_challenge_dailychallenge" (
                "challenge_ptr_id" bigint NOT NULL PRIMARY KEY REFERENCES "challenges_challenge" ("id"),
                "date" date NOT NULL UNIQUE
            );
        ''')


def reverse_migrate_sqlite_table(apps, schema_editor):
    """Reverse migration for SQLite."""
    if is_postgresql():
        return
    
    with schema_editor.connection.cursor() as cursor:
        cursor.execute('DROP TABLE IF EXISTS daily_challenge_dailychallenge;')
        cursor.execute('''
            CREATE TABLE "daily_challenge_dailychallenge" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "date" date NOT NULL UNIQUE,
                "challenge_id" bigint NOT NULL REFERENCES "challenges_challenge" ("id")
            );
        ''')


class Migration(migrations.Migration):

    dependencies = [
        ('daily_challenge', '0001_initial'),
        ('challenges', '0001_initial'),
    ]

    operations = [
        # Use SeparateDatabaseAndState to handle both PostgreSQL and SQLite
        migrations.SeparateDatabaseAndState(
            database_operations=[
                # For PostgreSQL: run custom SQL to alter the existing table
                migrations.RunPython(alter_for_postgresql, reverse_alter_for_postgresql),
                # For SQLite: recreate the table with the new schema
                migrations.RunPython(migrate_sqlite_table, reverse_migrate_sqlite_table),
            ],
            state_operations=[
                # Update Django's model state for all databases
                migrations.DeleteModel(
                    name='DailyChallenge',
                ),
                migrations.CreateModel(
                    name='DailyChallenge',
                    fields=[
                        ('challenge_ptr', models.OneToOneField(
                            auto_created=True,
                            on_delete=django.db.models.deletion.CASCADE,
                            parent_link=True,
                            primary_key=True,
                            serialize=False,
                            to='challenges.challenge',
                        )),
                        ('date', models.DateField(unique=True)),
                    ],
                    options={
                        'ordering': ['-date', '-id'],
                    },
                ),
            ],
        ),
    ]
