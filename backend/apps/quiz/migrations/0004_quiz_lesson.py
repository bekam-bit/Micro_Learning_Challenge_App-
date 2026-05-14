from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0001_initial'),
        ('quiz', '0003_question_question_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='lesson',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='quizzes',
                to='lessons.lesson',
            ),
        ),
    ]
