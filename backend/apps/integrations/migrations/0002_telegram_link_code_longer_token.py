from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("integrations", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="telegramlinkcode",
            name="code",
            field=models.CharField(max_length=64, unique=True),
        ),
    ]
