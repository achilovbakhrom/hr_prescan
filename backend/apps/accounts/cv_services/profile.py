import logging

from apps.accounts.models import CandidateProfile

logger = logging.getLogger(__name__)


def get_or_create_candidate_profile(*, user):
    """Get or create CandidateProfile for user."""
    profile, _ = CandidateProfile.objects.get_or_create(user=user)
    return profile


def calculate_profile_completeness(*, profile):
    """Return {score: 0-100, sections: {personal: bool, summary: bool, experience: bool, education: bool, skills: bool, languages: bool}}"""
    sections = {
        "personal": bool(profile.headline and profile.location),
        "summary": bool(profile.summary),
        "experience": profile.work_experiences.exists(),
        "education": profile.educations.exists(),
        "skills": profile.skills.exists(),
        "languages": profile.languages.exists(),
    }
    filled = sum(sections.values())
    total = len(sections)
    return {"score": round(filled / total * 100), "sections": sections}


def _populate_profile_from_parsed(*, profile, data):
    """Map AI-parsed data to profile models."""
    from apps.accounts.models import (
        CandidateLanguage,
        Certification,
        Education,
        WorkExperience,
    )
    from apps.common.models import Language, Skill

    # Update basic fields
    update_fields = []
    for field in ("headline", "summary", "location"):
        if data.get(field):
            setattr(profile, field, data[field])
            update_fields.append(field)
    if update_fields:
        profile.save(update_fields=[*update_fields, "updated_at"])

    # Work experiences
    for exp in data.get("work_experiences", []):
        try:
            from datetime import date

            WorkExperience.objects.create(
                profile=profile,
                company_name=exp.get("company_name", ""),
                position=exp.get("position", ""),
                employment_type=exp.get("employment_type", ""),
                location=exp.get("location", ""),
                start_date=exp.get("start_date") or date.today(),
                end_date=exp.get("end_date"),
                is_current=exp.get("is_current", False),
                description=exp.get("description", ""),
            )
        except Exception:
            logger.warning("Failed to create work experience from parsed CV", exc_info=True)

    # Educations
    for edu in data.get("educations", []):
        try:
            Education.objects.create(
                profile=profile,
                institution=edu.get("institution", ""),
                degree=edu.get("degree", ""),
                field_of_study=edu.get("field_of_study", ""),
                start_date=edu.get("start_date"),
                end_date=edu.get("end_date"),
                description=edu.get("description", ""),
            )
        except Exception:
            logger.warning("Failed to create education from parsed CV", exc_info=True)

    # Skills -- fuzzy match against DB
    skill_names = data.get("skills", [])
    if skill_names:
        from django.db.models import Q

        q = Q()
        for name in skill_names:
            q |= Q(name__iexact=name) | Q(slug__iexact=name.lower().replace(" ", "-"))
        matched = Skill.objects.filter(q)
        profile.skills.add(*matched)

    # Languages
    for lang in data.get("languages", []):
        try:
            lang_name = lang.get("language", "")
            lang_obj = Language.objects.filter(name__iexact=lang_name).first()
            if lang_obj:
                CandidateLanguage.objects.get_or_create(
                    profile=profile,
                    language=lang_obj,
                    defaults={"proficiency": lang.get("proficiency", "intermediate")},
                )
        except Exception:
            logger.warning("Failed to create language from parsed CV", exc_info=True)

    # Certifications
    for cert in data.get("certifications", []):
        try:
            Certification.objects.create(
                profile=profile,
                name=cert.get("name", ""),
                issuing_organization=cert.get("issuing_organization", ""),
                issue_date=cert.get("issue_date"),
            )
        except Exception:
            logger.warning("Failed to create certification from parsed CV", exc_info=True)
