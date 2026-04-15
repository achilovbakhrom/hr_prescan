from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("integrations", "0003_telegram_auth_code"),
    ]

    operations = [
        migrations.DeleteModel(
            name="TelegramAuthCode",
        ),
    ]
