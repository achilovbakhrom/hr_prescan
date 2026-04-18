from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0016_add_subscription_fields_to_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="companymembership",
            name="is_default",
            field=models.BooleanField(default=False),
        ),
    ]
