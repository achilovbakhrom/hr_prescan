from apps.common.models import Country


def resolve_country_display_name(country_code: str | None) -> str:
    normalized_code = (country_code or "").strip().upper()

    if not normalized_code:
        return ""

    if len(normalized_code) != 2:
        return (country_code or "").strip()

    country = Country.objects.filter(code=normalized_code).only("name").first()
    return country.name if country else normalized_code
