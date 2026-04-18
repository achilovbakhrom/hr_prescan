from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0014_change_is_open_to_work_default_false"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="language",
            field=models.CharField(
                choices=[("en", "English"), ("ru", "Russian"), ("uz", "Uzbek")],
                default="en",
                max_length=5,
            ),
        ),
    ]
