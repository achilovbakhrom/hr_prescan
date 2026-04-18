import secrets

from django.db import migrations, models


def generate_share_tokens(apps, schema_editor):
    CandidateProfile = apps.get_model("accounts", "CandidateProfile")
    for profile in CandidateProfile.objects.all():
        profile.share_token = secrets.token_urlsafe(24)
        profile.save(update_fields=["share_token"])


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0008_candidate_photo_cert_image_multiple_cvs"),
    ]

    operations = [
        migrations.AddField(
            model_name="candidateprofile",
            name="share_token",
            field=models.CharField(blank=True, default="", max_length=64),
        ),
        migrations.RunPython(generate_share_tokens, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="candidateprofile",
            name="share_token",
            field=models.CharField(blank=True, default="", max_length=64, unique=True),
        ),
    ]
