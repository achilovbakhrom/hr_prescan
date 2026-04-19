import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0015_user_language"),
        ("subscriptions", "0002_seed_default_plans"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="subscription_plan",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="users",
                to="subscriptions.subscriptionplan",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="subscription_status",
            field=models.CharField(
                choices=[
                    ("trial", "Trial"),
                    ("active", "Active"),
                    ("past_due", "Past Due"),
                    ("cancelled", "Cancelled"),
                ],
                default="trial",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="trial_ends_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
