from datetime import date

from django.db import migrations


def _date_range(start, end):
    if not start and not end:
        return ""
    start_label = start.strftime("%b %Y") if start else ""
    end_label = end.strftime("%b %Y") if end else "Present"
    return f"{start_label} - {end_label}".strip(" -")


def _experience_years(experiences):
    total_days = 0
    today = date.today()
    for item in experiences:
        if not item.start_date:
            continue
        end = today if item.is_current or item.end_date is None else item.end_date
        total_days += max((end - item.start_date).days, 0)
    return round(total_days / 365, 1) if total_days else None


def _snapshot_text(user, profile, data):
    lines = [f"{user.first_name} {user.last_name}".strip() or user.email]
    if profile.headline:
        lines.append(profile.headline)
    if data["summary"]:
        lines.extend(["", "Summary", data["summary"]])
    if data["skills"]:
        lines.extend(["", "Skills", ", ".join(data["skills"])])
    for item in data["experience"]:
        lines.extend(["", "Experience", f"{item['role']} at {item['company']} {item['duration']}".strip()])
        if item["description"]:
            lines.append(item["description"])
    for item in data["education"]:
        lines.extend(["", "Education", f"{item['degree']} {item['field']} at {item['institution']} {item['year']}".strip()])
    return "\n".join(line for line in lines if line)


def backfill_profile_resume_snapshots(apps, schema_editor):
    Application = apps.get_model("applications", "Application")
    CandidateProfile = apps.get_model("accounts", "CandidateProfile")

    applications = Application.objects.filter(candidate__isnull=False, cv_parsed_data={}).select_related("candidate")
    for application in applications.iterator():
        profile = CandidateProfile.objects.filter(user_id=application.candidate_id).first()
        if profile is None:
            continue
        experiences = list(profile.work_experiences.all())
        data = {
            "contacts": {
                "email": application.candidate.email,
                "phone": application.candidate.phone,
                "location": profile.location or None,
                "linkedin": profile.linkedin_url or None,
                "github": profile.github_url or None,
                "website": profile.website_url or None,
                "telegram": application.candidate.telegram_username or None,
            },
            "skills": [skill.name for skill in profile.skills.all()],
            "experience_years": _experience_years(experiences),
            "experience": [
                {
                    "company": item.company_name,
                    "role": item.position,
                    "position": item.position,
                    "duration": _date_range(item.start_date, None if item.is_current else item.end_date),
                    "description": item.description,
                }
                for item in experiences
            ],
            "education": [
                {
                    "degree": item.degree,
                    "field": item.field_of_study,
                    "institution": item.institution,
                    "year": str((item.end_date or item.start_date).year) if (item.end_date or item.start_date) else "",
                }
                for item in profile.educations.all()
            ],
            "languages": [
                {"language": item.language.name, "level": item.proficiency}
                for item in profile.languages.select_related("language").all()
            ],
            "certifications": [item.name for item in profile.certifications.all() if item.name],
            "summary": profile.summary or profile.headline,
            "content_language": application.candidate.language or "en",
        }
        if not any([data["summary"], data["skills"], data["experience"], data["education"], data["languages"], data["certifications"]]):
            continue
        application.cv_parsed_text = _snapshot_text(application.candidate, profile, data)[:50000]
        application.cv_parsed_data = data
        application.cv_summary_translations = {data["content_language"]: data["summary"]} if data["summary"] else {}
        application.save(update_fields=["cv_parsed_text", "cv_parsed_data", "cv_summary_translations", "updated_at"])


class Migration(migrations.Migration):
    dependencies = [
        ("applications", "0007_backfill_candidate_platform_cvs"),
    ]

    operations = [
        migrations.RunPython(backfill_profile_resume_snapshots, migrations.RunPython.noop),
    ]
