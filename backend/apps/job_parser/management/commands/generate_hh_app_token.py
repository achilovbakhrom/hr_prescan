from django.core.management.base import BaseCommand, CommandError

from apps.common.exceptions import ApplicationError
from apps.job_parser.models import ParsedVacancySource
from apps.job_parser.services.hh_auth import request_hh_application_access_token


class Command(BaseCommand):
    help = "Generate a HeadHunter application access token from configured client credentials."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source-type",
            choices=[ParsedVacancySource.Type.HH_RU, ParsedVacancySource.Type.HH_UZ],
            default=ParsedVacancySource.Type.HH_UZ,
            help="HeadHunter site to generate a token for.",
        )
        parser.add_argument(
            "--env-name",
            default="",
            help="Environment variable name to print before the token. Defaults to the site-specific token env.",
        )

    def handle(self, *args, **options):
        source_type = options["source_type"]
        env_name = options["env_name"] or ("HH_UZ_ACCESS_TOKEN" if source_type == "hh_uz" else "HH_RU_ACCESS_TOKEN")
        try:
            token = request_hh_application_access_token(source_type=source_type)
        except ApplicationError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(f"{env_name}={token}")
