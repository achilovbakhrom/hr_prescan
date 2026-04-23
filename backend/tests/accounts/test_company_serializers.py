import pytest

from apps.accounts.apis.user_companies import UserCompanyListOutputSerializer
from apps.accounts.serializers import CompanyOutputSerializer
from apps.common.serializers_admin import AdminCompanyDetailOutputSerializer
from apps.common.models import Country
from tests.factories import CompanyFactory, CompanyMembershipFactory


@pytest.mark.django_db
def test_company_output_serializer_returns_full_country_name():
    Country.objects.create(code="UZ", name="Uzbekistan", name_ru="Узбекистан", name_uz="O'zbekiston")
    company = CompanyFactory(country="UZ")

    data = CompanyOutputSerializer(company).data

    assert data["country"] == "Uzbekistan"


@pytest.mark.django_db
def test_user_company_list_serializer_normalizes_country_code_case():
    Country.objects.create(code="RU", name="Russia", name_ru="Россия", name_uz="Rossiya")
    membership = CompanyMembershipFactory()
    membership.company.country = "Ru"
    membership.company.save(update_fields=["country"])

    data = UserCompanyListOutputSerializer(membership).data

    assert data["country"] == "Russia"


@pytest.mark.django_db
def test_admin_company_detail_serializer_returns_full_country_name():
    Country.objects.create(code="KZ", name="Kazakhstan", name_ru="Казахстан", name_uz="Qozog'iston")
    company = CompanyFactory(country="KZ")

    data = AdminCompanyDetailOutputSerializer(company).data

    assert data["country"] == "Kazakhstan"
