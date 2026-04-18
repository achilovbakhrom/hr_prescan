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

    # Salary / employment preferences (accept None/empty values as unset)
    valid_employment_types = {choice[0] for choice in CandidateProfile.EmploymentType.choices}
    employment_type = data.get("desired_employment_type")
    if employment_type in valid_employment_types:
        profile.desired_employment_type = employment_type
        update_fields.append("desired_employment_type")

    for numeric_field in ("desired_salary_min", "desired_salary_max"):
        value = data.get(numeric_field)
        if value is not None:
            try:
                setattr(profile, numeric_field, value)
                update_fields.append(numeric_field)
            except (TypeError, ValueError):
                logger.warning("Invalid %s value from parsed CV: %r", numeric_field, value)

    currency = data.get("desired_salary_currency")
    if currency:
        profile.desired_salary_currency = currency[:3].upper()
        update_fields.append("desired_salary_currency")

    if "desired_salary_negotiable" in data:
        profile.desired_salary_negotiable = bool(data.get("desired_salary_negotiable"))
        update_fields.append("desired_salary_negotiable")

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
