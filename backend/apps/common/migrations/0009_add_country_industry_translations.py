from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0008_seed_skills"),
    ]

    operations = [
        migrations.AddField(
            model_name="country",
            name="name_ru",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="country",
            name="name_uz",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="industry",
            name="name_ru",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="industry",
            name="name_uz",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
    ]
