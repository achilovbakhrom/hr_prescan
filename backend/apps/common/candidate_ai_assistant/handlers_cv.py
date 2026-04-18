import logging

logger = logging.getLogger(__name__)


def _handle_get_my_cv_status(*, user, params):
    from apps.accounts.cv_services import (
        calculate_profile_completeness,
        get_or_create_candidate_profile,
    )

    profile = get_or_create_candidate_profile(user=user)
    completeness = calculate_profile_completeness(profile=profile)
    return {
        "success": True,
        "message": "Current CV status retrieved.",
        "data": {
            "completeness": completeness,
            "headline": profile.headline or "",
            "summary": profile.summary or "",
            "location": profile.location or "",
            "desired_employment_type": profile.desired_employment_type or "",
            "desired_salary_min": str(profile.desired_salary_min) if profile.desired_salary_min else None,
            "desired_salary_max": str(profile.desired_salary_max) if profile.desired_salary_max else None,
            "desired_salary_currency": profile.desired_salary_currency or "",
            "work_experience_count": profile.work_experiences.count(),
            "education_count": profile.educations.count(),
            "skill_count": profile.skills.count(),
            "language_count": profile.languages.count(),
        },
        "action": "get_my_cv_status",
    }


def _handle_build_my_cv(*, user, params):
    from apps.accounts.cv_services import (
        _populate_profile_from_parsed,
        calculate_profile_completeness,
        get_or_create_candidate_profile,
    )

    payload = {
        "headline": params.get("headline", ""),
        "summary": params.get("summary", ""),
        "location": params.get("location", ""),
        "desired_employment_type": params.get("desired_employment_type", ""),
        "desired_salary_min": params.get("desired_salary_min"),
        "desired_salary_max": params.get("desired_salary_max"),
        "desired_salary_currency": params.get("desired_salary_currency", ""),
        "desired_salary_negotiable": params.get("desired_salary_negotiable"),
        "work_experiences": params.get("work_experiences") or [],
        "educations": params.get("educations") or [],
        "skills": params.get("skills") or [],
        "languages": params.get("languages") or [],
        "certifications": params.get("certifications") or [],
    }

    if not any(
        [
            payload["headline"],
            payload["work_experiences"],
            payload["educations"],
            payload["skills"],
        ]
    ):
        return {
            "success": False,
            "message": "Please collect at least a job title or some experience before saving.",
            "data": {},
            "action": "build_my_cv",
        }

    profile = get_or_create_candidate_profile(user=user)
    try:
        _populate_profile_from_parsed(profile=profile, data=payload)
    except Exception as exc:
        logger.exception("build_my_cv failed")
        return {
            "success": False,
            "message": f"Failed to save CV: {exc}",
            "data": {},
            "action": "build_my_cv",
        }

    completeness = calculate_profile_completeness(profile=profile)
    return {
        "success": True,
        "message": "Your CV has been saved.",
        "data": {"completeness": completeness},
        "action": "build_my_cv",
    }


def _handle_generate_cv_pdf(*, user, params):
    from apps.accounts.cv_services import (
        generate_cv_pdf,
        get_or_create_candidate_profile,
    )

    template_name = params.get("template_name") or "classic"
    cv_name = params.get("cv_name") or "My CV"

    profile = get_or_create_candidate_profile(user=user)
    try:
        result = generate_cv_pdf(profile=profile, template_name=template_name, cv_name=cv_name)
    except Exception as exc:
        logger.exception("generate_cv_pdf failed")
        return {
            "success": False,
            "message": f"Failed to generate CV PDF: {exc}",
            "data": {},
            "action": "generate_cv_pdf",
        }

    return {
        "success": True,
        "message": "Your CV PDF is ready.",
        "data": result if isinstance(result, dict) else {"result": str(result)},
        "action": "generate_cv_pdf",
    }
