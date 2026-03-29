from apps.accounts.models import Company
from apps.common.exceptions import ApplicationError
from apps.common.messages import MSG_EMPLOYER_HAS_VACANCIES
from apps.vacancies.models import EmployerCompany

from .company_info import detect_language, parse_company_info_from_file, parse_company_info_from_url


def create_employer(*, company: Company, name: str, **kwargs: object) -> EmployerCompany:
    """Create a manually-entered employer company."""
    return EmployerCompany.objects.create(company=company, name=name, **kwargs)


def create_employer_from_file(*, company: Company, name: str, file_obj: object) -> EmployerCompany:
    """Create an employer company with description parsed from an uploaded file."""
    description = parse_company_info_from_file(file_obj=file_obj)
    detected_lang = detect_language(description)
    return EmployerCompany.objects.create(
        company=company,
        name=name,
        description=description,
        description_translations={detected_lang: description},
        source=EmployerCompany.Source.FILE,
    )


def create_employer_from_url(*, company: Company, name: str, url: str) -> EmployerCompany:
    """Create an employer company with description parsed from a website URL."""
    description = parse_company_info_from_url(url=url)
    detected_lang = detect_language(description)
    return EmployerCompany.objects.create(
        company=company,
        name=name,
        description=description,
        description_translations={detected_lang: description},
        source=EmployerCompany.Source.WEBSITE,
    )


def update_employer(*, employer: EmployerCompany, data: dict) -> EmployerCompany:
    """Update allowed employer company fields."""
    allowed_fields = {"name", "industry", "logo", "website", "description"}
    update_fields: list[str] = []
    for field, value in data.items():
        if field in allowed_fields:
            setattr(employer, field, value)
            update_fields.append(field)
    if update_fields:
        update_fields.append("updated_at")
        employer.save(update_fields=update_fields)
    return employer


def delete_employer(*, employer: EmployerCompany) -> None:
    """Delete an employer company. Raises if it has linked vacancies."""
    if employer.vacancies.exists():
        raise ApplicationError(str(MSG_EMPLOYER_HAS_VACANCIES))
    employer.delete()
