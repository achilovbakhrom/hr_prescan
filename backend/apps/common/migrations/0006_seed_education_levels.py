from django.db import migrations


def seed_education_levels(apps, schema_editor):
    EducationLevel = apps.get_model("common", "EducationLevel")
    levels = [
        ("high-school", "High School", 1),
        ("associate", "Associate Degree", 2),
        ("bachelor", "Bachelor's Degree", 3),
        ("master", "Master's Degree", 4),
        ("phd", "Doctorate / PhD", 5),
        ("professional-certificate", "Professional Certificate", 6),
        ("bootcamp", "Bootcamp / Course", 7),
        ("self-taught", "Self-Taught", 8),
    ]
    EducationLevel.objects.bulk_create(
        [EducationLevel(slug=s, name=n, order=o) for s, n, o in levels],
        ignore_conflicts=True,
    )


def reverse_seed(apps, schema_editor):
    EducationLevel = apps.get_model("common", "EducationLevel")
    EducationLevel.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0005_create_skill_language_education_level"),
    ]

    operations = [
        migrations.RunPython(seed_education_levels, reverse_seed),
    ]
