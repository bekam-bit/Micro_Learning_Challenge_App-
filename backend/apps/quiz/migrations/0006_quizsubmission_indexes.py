from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0005_quizsubmission'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='quizsubmission',
            index=models.Index(fields=['user', 'is_submitted'], name='quizsub_user_submitted_idx'),
        ),
        migrations.AddIndex(
            model_name='quizsubmission',
            index=models.Index(fields=['quiz', 'is_submitted'], name='quizsub_quiz_submitted_idx'),
        ),
        migrations.AddIndex(
            model_name='quizsubmission',
            index=models.Index(fields=['submitted_at'], name='quizsub_submitted_at_idx'),
        ),
    ]
