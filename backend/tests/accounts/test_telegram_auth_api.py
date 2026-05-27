import time
from unittest.mock import patch

from rest_framework.test import APIClient

from apps.accounts.models import CandidateProfile, Company, CompanyMembership, User
from apps.integrations.telegram_bot.hr.onboarding import get_or_create_hr_bot_user
from apps.vacancies.models import Vacancy


def test_telegram_login_merges_hr_placeholder_workspace_into_candidate_account():
    telegram_id = 438237137
    candidate = User.objects.create_user(
        email=f"tg_{telegram_id}@telegram.local",
        password=None,
        first_name="Telegram",
        last_name="Candidate",
        phone="998919767777",
        role=User.Role.CANDIDATE,
        telegram_id=telegram_id,
        telegram_username="old_username",
        email_verified=True,
    )
    placeholder = get_or_create_hr_bot_user(
        telegram_id=telegram_id,
        telegram_username="abk0306",
        first_name="Telegram",
        last_name="HR",
        language=User.Language.RU,
    )
    company = Company.objects.create(
        account_owner=placeholder,
        name="My Company",
        size=Company.Size.SMALL,
        country="Uzbekistan",
    )
    CompanyMembership.objects.create(user=placeholder, company=company, role=User.Role.ADMIN, is_default=True)
    placeholder.company = company
    placeholder.onboarding_completed = True
    placeholder.save(update_fields=["company", "onboarding_completed", "updated_at"])
    vacancy = Vacancy.objects.create(
        company=company,
        created_by=placeholder,
        title="Telegram Vacancy",
        description="Created from Telegram",
        status=Vacancy.Status.PUBLISHED,
    )

    client = APIClient()
    with patch("apps.accounts.apis.telegram_auth.TelegramAuthApi._verify_telegram_hash", return_value=True):
        response = client.post(
            "/api/auth/telegram/",
            {
                "id": telegram_id,
                "first_name": "Telegram",
                "last_name": "Candidate",
                "username": "abk0306",
                "auth_date": int(time.time()),
                "hash": "test",
            },
            format="json",
        )

    assert response.status_code == 200
    candidate.refresh_from_db()
    placeholder.refresh_from_db()
    company.refresh_from_db()
    vacancy.refresh_from_db()

    assert placeholder.is_active is False
    assert placeholder.telegram_id is None
    assert candidate.telegram_id == telegram_id
    assert candidate.telegram_username == "abk0306"
    assert candidate.language == User.Language.RU
    assert candidate.role == User.Role.ADMIN
    assert candidate.active_mode == User.ActiveMode.CANDIDATE
    assert CandidateProfile.objects.filter(user=candidate).exists()
    assert company.account_owner == candidate
    assert vacancy.created_by == candidate
    assert CompanyMembership.objects.filter(user=candidate, company=company, is_default=True).exists()

    client.force_authenticate(user=candidate)
    modes_response = client.get("/api/auth/modes/")

    assert modes_response.status_code == 200
    assert set(modes_response.data["available_modes"]) == {User.ActiveMode.HR, User.ActiveMode.CANDIDATE}
