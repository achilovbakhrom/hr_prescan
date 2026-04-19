from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0021_drop_subscription_fields_from_company"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="account_owner",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name="account_members",
                to="accounts.user",
            ),
        ),
    ]
