import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def generate_keywords_task(vacancy_id: str) -> None:
    """Generate AI keywords and update search vector for a vacancy."""
    from apps.vacancies.models import Vacancy
    from apps.vacancies.services import generate_vacancy_keywords, update_vacancy_search_vector

    try:
        vacancy = Vacancy.objects.get(id=vacancy_id)
    except Vacancy.DoesNotExist:
        logger.warning("Vacancy %s not found for keyword generation.", vacancy_id)
        return

    try:
        generate_vacancy_keywords(vacancy=vacancy)
        update_vacancy_search_vector(vacancy=vacancy)
        logger.info("Keywords generated and search vector updated for vacancy %s.", vacancy_id)
    except Exception:
        logger.exception("Failed to generate keywords for vacancy %s.", vacancy_id)
