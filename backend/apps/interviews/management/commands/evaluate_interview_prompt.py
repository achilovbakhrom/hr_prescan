import json

from django.core.management.base import BaseCommand, CommandError

from apps.interviews.models import Interview
from apps.interviews.services import evaluate_interview_prompt


class Command(BaseCommand):
    help = "Evaluate an interview prompt with the configured Gemini model."

    def add_arguments(self, parser):
        parser.add_argument("interview_id", help="Interview/session UUID to evaluate")

    def handle(self, *args, **options):
        interview_id = options["interview_id"]
        interview = (
            Interview.objects.select_related(
                "application",
                "application__vacancy",
                "application__vacancy__company",
                "application__candidate",
            )
            .filter(id=interview_id)
            .first()
        )
        if interview is None:
            raise CommandError(f"Interview not found: {interview_id}")

        result = evaluate_interview_prompt(interview=interview)
        self.stdout.write(json.dumps(result, indent=2, ensure_ascii=False))
