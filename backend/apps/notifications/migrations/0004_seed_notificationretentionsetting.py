from django.db import migrations


def seed_notification_retention_setting(apps, schema_editor):
    NotificationRetentionSetting = apps.get_model('notifications', 'NotificationRetentionSetting')
    NotificationRetentionSetting.objects.get_or_create(
        singleton_key=1,
        defaults={
            'enabled': True,
            'retention_days': 30,
        },
    )


def reverse_seed_notification_retention_setting(apps, schema_editor):
    NotificationRetentionSetting = apps.get_model('notifications', 'NotificationRetentionSetting')
    NotificationRetentionSetting.objects.filter(singleton_key=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0003_notificationretentionsetting'),
    ]

    operations = [
        migrations.RunPython(seed_notification_retention_setting, reverse_seed_notification_retention_setting),
    ]
