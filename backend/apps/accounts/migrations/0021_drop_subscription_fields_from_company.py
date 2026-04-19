from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0020_alter_user_company_on_delete_set_null"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="company",
            name="subscription_plan",
        ),
        migrations.RemoveField(
            model_name="company",
            name="subscription_status",
        ),
        migrations.RemoveField(
            model_name="company",
            name="trial_ends_at",
        ),
    ]
