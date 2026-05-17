from uuid import UUID

from django.db.models import Exists, OuterRef, Q, QuerySet

from apps.accounts.models import User
from apps.accounts.selectors import get_user_live_company_ids
from apps.applications.models import Application, HRCandidate


def _visible_candidate_applications(*, user: User, candidate: HRCandidate) -> QuerySet[Application]:
    return (
        Application.objects.filter(
            vacancy__company_id__in=get_user_live_company_ids(user=user),
            candidate_email__iexact=candidate.candidate_email_normalized,
            is_deleted=False,
        )
        .select_related("candidate", "vacancy", "vacancy__company")
        .prefetch_related("sessions", "hiring_manager_feedback")
        .order_by("-created_at")
    )


def get_hr_candidates_filtered(
    *,
    user: User,
    search: str | None = None,
    ordering: str = "-last_activity_at",
) -> QuerySet[HRCandidate]:
    company_ids = get_user_live_company_ids(user=user)
    visible_applications = Application.objects.filter(
        vacancy__company_id__in=company_ids,
        candidate_email__iexact=OuterRef("candidate_email_normalized"),
        is_deleted=False,
    )
    allowed_orderings = {"-last_activity_at", "last_activity_at", "candidate_name", "-candidate_name"}
    if ordering not in allowed_orderings:
        ordering = "-last_activity_at"

    qs = HRCandidate.objects.filter(
        account_owner=user.effective_account_owner,
        is_deleted=False,
    ).filter(Exists(visible_applications))

    if search:
        vacancy_match = visible_applications.filter(vacancy__title__icontains=search)
        qs = qs.annotate(_vacancy_match=Exists(vacancy_match)).filter(
            Q(candidate_name__icontains=search)
            | Q(candidate_email__icontains=search)
            | Q(candidate_phone__icontains=search)
            | Q(_vacancy_match=True)
        )

    return qs.select_related("candidate", "latest_application").order_by(ordering)


def get_hr_candidate_by_id(*, user: User, candidate_id: UUID) -> HRCandidate | None:
    return get_hr_candidates_filtered(user=user).filter(id=candidate_id).first()


def get_hr_candidate_applications(*, user: User, candidate: HRCandidate) -> QuerySet[Application]:
    return _visible_candidate_applications(user=user, candidate=candidate)
