from apps.applications.models import Application, ApplicationEvent, HiringManagerFeedback


def create_hiring_manager_feedback(
    *,
    application: Application,
    reviewer_name: str,
    reviewer_role: str = "",
    recommendation: str,
    rating: int | None = None,
    comment: str = "",
) -> HiringManagerFeedback:
    """Persist hiring-manager feedback from a candidate share link."""
    feedback = HiringManagerFeedback.objects.create(
        application=application,
        reviewer_name=reviewer_name.strip(),
        reviewer_role=reviewer_role.strip(),
        recommendation=recommendation,
        rating=rating,
        comment=comment.strip(),
    )
    ApplicationEvent.objects.create(
        application=application,
        event_type=ApplicationEvent.EventType.HIRING_MANAGER_FEEDBACK,
        actor_name=feedback.reviewer_name,
        message=f"Hiring manager recommended: {feedback.recommendation}",
        metadata={"feedback_id": str(feedback.id), "rating": feedback.rating},
    )
    return feedback
