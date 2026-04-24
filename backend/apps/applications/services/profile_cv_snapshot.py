from datetime import date

from apps.accounts.models import CandidateProfile, User
from apps.applications.models import Application


def build_candidate_profile_cv_snapshot(*, candidate: User | None) -> dict | None:
    if candidate is None:
        return None

    profile = (
        CandidateProfile.objects.select_related("user")
        .prefetch_related(
            "skills",
            "work_experiences",
            "educations__education_level",
            "languages__language",
            "certifications",
        )
        .filter(user=candidate)
        .first()
    )
    if profile is None:
        return None

    data = {
        "contacts": _contacts(candidate, profile),
        "skills": [skill.name for skill in profile.skills.all()],
        "experience_years": _experience_years(profile),
        "experience": [_experience_item(item) for item in profile.work_experiences.all()],
        "education": [_education_item(item) for item in profile.educations.all()],
        "languages": [
            {"language": item.language.name, "level": item.get_proficiency_display()}
            for item in profile.languages.all()
        ],
        "certifications": [item.name for item in profile.certifications.all() if item.name],
        "summary": profile.summary or profile.headline,
        "content_language": candidate.language or "en",
    }
    if not _has_resume_data(data):
        return None
    return {
        "text": _snapshot_text(candidate=candidate, profile=profile, data=data),
        "data": data,
        "summary_translations": {data["content_language"]: data["summary"]} if data["summary"] else {},
    }


def apply_candidate_profile_cv_snapshot(*, application: Application, snapshot: dict | None) -> bool:
    if snapshot is None:
        return False
    application.cv_parsed_text = snapshot["text"][:50000]
    application.cv_parsed_data = snapshot["data"]
    application.cv_summary_translations = snapshot["summary_translations"]
    application.save(update_fields=["cv_parsed_text", "cv_parsed_data", "cv_summary_translations", "updated_at"])
    return True


def _contacts(candidate: User, profile: CandidateProfile) -> dict:
    return {
        "email": candidate.email,
        "phone": candidate.phone or None,
        "location": profile.location or None,
        "linkedin": profile.linkedin_url or None,
        "github": profile.github_url or None,
        "website": profile.website_url or None,
        "telegram": candidate.telegram_username or None,
    }


def _experience_item(item) -> dict:
    return {
        "company": item.company_name,
        "role": item.position,
        "position": item.position,
        "duration": _date_range(item.start_date, None if item.is_current else item.end_date),
        "description": item.description,
    }


def _education_item(item) -> dict:
    level = item.education_level.name if item.education_level else ""
    return {
        "degree": item.degree or level,
        "field": item.field_of_study,
        "institution": item.institution,
        "year": str((item.end_date or item.start_date).year) if (item.end_date or item.start_date) else "",
    }


def _date_range(start, end) -> str:
    if not start and not end:
        return ""
    start_label = start.strftime("%b %Y") if start else ""
    end_label = end.strftime("%b %Y") if end else "Present"
    return f"{start_label} - {end_label}".strip(" -")


def _experience_years(profile: CandidateProfile) -> float | None:
    total_days = 0
    today = date.today()
    for item in profile.work_experiences.all():
        if not item.start_date:
            continue
        end = today if item.is_current or item.end_date is None else item.end_date
        total_days += max((end - item.start_date).days, 0)
    return round(total_days / 365, 1) if total_days else None


def _has_resume_data(data: dict) -> bool:
    return any(
        [
            data["summary"],
            data["skills"],
            data["experience"],
            data["education"],
            data["languages"],
            data["certifications"],
        ]
    )


def _snapshot_text(*, candidate: User, profile: CandidateProfile, data: dict) -> str:
    lines = [candidate.full_name or candidate.email]
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
        education = f"{item['degree']} {item['field']} at {item['institution']} {item['year']}".strip()
        lines.extend(["", "Education", education])
    if data["languages"]:
        languages = ", ".join(f"{item['language']} {item['level']}".strip() for item in data["languages"])
        lines.extend(["", "Languages", languages])
    if data["certifications"]:
        lines.extend(["", "Certifications", ", ".join(data["certifications"])])
    return "\n".join(line for line in lines if line)
