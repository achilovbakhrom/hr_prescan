import logging

from celery import shared_task

from apps.applications.services import (
    analyze_cv_with_ai,
    calculate_match_score,
    process_cv_text,
)

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=10)
def process_cv(self, application_id: str) -> None:
    """Extract text from CV, then chain AI analysis and match scoring."""
    try:
        process_cv_text(application_id=application_id)
    except Exception as exc:
        logger.exception("process_cv failed for %s", application_id)
        raise self.retry(exc=exc) from exc
    analyze_cv.delay(application_id)


@shared_task(bind=True, max_retries=2, default_retry_delay=10)
def analyze_cv(self, application_id: str) -> None:
    """Run AI analysis on CV parsed text, then chain match scoring."""
    try:
        analyze_cv_with_ai(application_id=application_id)
    except Exception as exc:
        logger.exception("analyze_cv failed for %s", application_id)
        raise self.retry(exc=exc) from exc
    calculate_cv_match.delay(application_id)


@shared_task(bind=True, max_retries=2, default_retry_delay=10)
def calculate_cv_match(self, application_id: str) -> None:
    """Calculate match score between CV and vacancy requirements."""
    try:
        calculate_match_score(application_id=application_id)
    except Exception as exc:
        logger.exception("calculate_cv_match failed for %s", application_id)
        raise self.retry(exc=exc) from exc
