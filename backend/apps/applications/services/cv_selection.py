from apps.accounts.models import CandidateCV, User


def get_candidate_platform_cv(*, candidate: User | None) -> tuple[str, str]:
    """Return the candidate's active/latest generated platform CV path and name."""
    if candidate is None:
        return "", ""

    cv = (
        CandidateCV.objects.filter(profile__user=candidate)
        .exclude(file="")
        .order_by("-is_active", "-created_at")
        .first()
    )
    if cv is None:
        return "", ""
    return cv.file, cv.name
