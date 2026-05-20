from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("notifications", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="type",
            field=models.CharField(
                choices=[
                    ("application_received", "Application Received"),
                    ("interview_scheduled", "Interview Scheduled"),
                    ("interview_completed", "Interview Completed"),
                    ("interview_reminder", "Interview Reminder"),
                    ("status_changed", "Status Changed"),
                    ("invitation_received", "Invitation Received"),
                    ("direct_message", "Direct Message"),
                    ("system", "System"),
                ],
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="delivered_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="message",
            name="delivery_channel",
            field=models.CharField(
                choices=[("web", "Web"), ("telegram", "Telegram")],
                default="web",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="delivery_failure_reason",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="message",
            name="delivery_status",
            field=models.CharField(
                choices=[("pending", "Pending"), ("delivered", "Delivered"), ("failed", "Failed")],
                default="pending",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="message",
            name="telegram_message_id",
            field=models.CharField(blank=True, default="", max_length=64),
        ),
    ]
