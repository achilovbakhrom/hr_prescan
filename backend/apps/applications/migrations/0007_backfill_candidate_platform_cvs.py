from django.db import migrations


def backfill_candidate_platform_cvs(apps, schema_editor):
    Application = apps.get_model("applications", "Application")
    CandidateCV = apps.get_model("accounts", "CandidateCV")

    applications = Application.objects.filter(
        candidate_id__isnull=False,
        cv_file="",
    ).only("id", "candidate_id", "cv_file", "cv_original_filename")
    for application in applications.iterator():
        cv = (
            CandidateCV.objects.filter(profile__user_id=application.candidate_id)
            .exclude(file="")
            .order_by("-is_active", "-created_at")
            .first()
        )
        if cv is None:
            continue

        application.cv_file = cv.file
        application.cv_original_filename = cv.name
        application.save(update_fields=["cv_file", "cv_original_filename", "updated_at"])


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0024_rework_invitation_to_account"),
        ("applications", "0006_add_translation_fields"),
    ]

    operations = [
        migrations.RunPython(backfill_candidate_platform_cvs, migrations.RunPython.noop),
    ]
