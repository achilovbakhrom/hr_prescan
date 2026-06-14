from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("applications", "0012_hrcandidate"),
    ]

    operations = [
        migrations.AddField(
            model_name="application",
            name="profile_photo",
            field=models.CharField(blank=True, default="", max_length=500),
        ),
        migrations.AddField(
            model_name="application",
            name="linkedin_url",
            field=models.CharField(blank=True, default="", max_length=500),
        ),
        migrations.AddField(
            model_name="application",
            name="cover_note",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="application",
            name="prescreen_consent",
            field=models.BooleanField(default=False),
        ),
    ]
