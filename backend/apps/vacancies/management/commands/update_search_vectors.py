import logging

from django.core.management.base import BaseCommand

from apps.vacancies.models import Vacancy
from apps.vacancies.services import generate_vacancy_keywords, update_vacancy_search_vector

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Generate AI keywords and update search vectors for all non-deleted vacancies."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-keywords",
            action="store_true",
            default=False,
            help="Only update search vectors without regenerating AI keywords.",
        )

    def handle(self, *args, **options):
        skip_keywords = options["skip_keywords"]
        vacancies = Vacancy.objects.filter(is_deleted=False)
        total = vacancies.count()
        self.stdout.write(f"Processing {total} vacancies...")

        success = 0
        failed = 0

        for vacancy in vacancies.iterator():
            try:
                if not skip_keywords:
                    generate_vacancy_keywords(vacancy=vacancy)
                update_vacancy_search_vector(vacancy=vacancy)
                success += 1
                self.stdout.write(f"  [{success}/{total}] {vacancy.title} — OK")
            except Exception:
                failed += 1
                logger.exception("Failed to process vacancy %s", vacancy.id)
                self.stderr.write(f"  [{success + failed}/{total}] {vacancy.title} — FAILED")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Success: {success}, Failed: {failed}, Total: {total}"
            )
        )
