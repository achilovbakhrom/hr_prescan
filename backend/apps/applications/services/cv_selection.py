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


def is_candidate_platform_cv_file(*, candidate: User | None, cv_file_path: str) -> bool:
    if candidate is None or not cv_file_path:
        return False
    return CandidateCV.objects.filter(profile__user=candidate, file=cv_file_path).exists()
