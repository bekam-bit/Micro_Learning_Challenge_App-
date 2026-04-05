from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0002_answer_explanation'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='question_type',
            field=models.CharField(
                choices=[
                    ('single_choice', 'Single Choice'),
                    ('multiple_choice', 'Multiple Choice'),
                    ('true_false', 'True / False'),
                ],
                default='single_choice',
                max_length=30,
            ),
        ),
    ]
