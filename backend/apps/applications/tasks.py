from celery import shared_task

from apps.applications.services import (
    analyze_cv_with_ai,
    calculate_match_score,
    process_cv_text,
)


@shared_task
def process_cv(application_id: str) -> None:
    """Extract text from CV, then chain AI analysis and match scoring."""
    process_cv_text(application_id=application_id)
    analyze_cv.delay(application_id)


@shared_task
def analyze_cv(application_id: str) -> None:
    """Run AI analysis on CV parsed text, then chain match scoring."""
    analyze_cv_with_ai(application_id=application_id)
    calculate_cv_match.delay(application_id)


@shared_task
def calculate_cv_match(application_id: str) -> None:
    """Calculate match score between CV and vacancy requirements."""
    calculate_match_score(application_id=application_id)
