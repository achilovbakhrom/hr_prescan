from unittest.mock import patch

import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from apps.accounts.models import CompanyMembership, User
from apps.accounts.permissions import HRPermissions
from apps.common.exceptions import ApplicationError
from apps.notifications.apis import HRMessageListApi
from apps.notifications.models import Message, Notification
from apps.notifications.services import NO_PLATFORM_INBOX_MESSAGE, send_candidate_message
from tests.factories import ApplicationFactory, CompanyFactory, UserFactory, VacancyFactory


def _hr_user_with_company():
    company = CompanyFactory()
    user = UserFactory(company=company, role=User.Role.HR, hr_permissions=[HRPermissions.MANAGE_CANDIDATES])
    CompanyMembership.objects.create(
        user=user,
        company=company,
        role=User.Role.HR,
        hr_permissions=[HRPermissions.MANAGE_CANDIDATES],
        is_default=True,
    )
    return user, company


def test_telegram_linked_candidate_receives_stored_message_and_telegram_delivery():
    hr_user, company = _hr_user_with_company()
    candidate = UserFactory(company=None, role=User.Role.CANDIDATE, telegram_id=998877)
    application = ApplicationFactory(vacancy=VacancyFactory(company=company, created_by=hr_user), candidate=candidate)

    with patch("apps.integrations.telegram_bot.client.requests.post") as post_mock:
        post_mock.return_value.json.return_value = {"ok": True, "result": {"message_id": 42}}
        message = send_candidate_message(sender=hr_user, application=application, content="Hi *Alex*_")

    message.refresh_from_db()
    assert message.delivery_channel == Message.DeliveryChannel.TELEGRAM
    assert message.delivery_status == Message.DeliveryStatus.DELIVERED
    assert message.telegram_message_id == "42"
    assert Notification.objects.filter(user=candidate, type=Notification.Type.DIRECT_MESSAGE).exists()
    payload = post_mock.call_args.kwargs["json"]
    assert payload["chat_id"] == candidate.telegram_id
    assert "parse_mode" not in payload


def test_web_only_candidate_receives_stored_message_and_notification():
    hr_user, company = _hr_user_with_company()
    candidate = UserFactory(company=None, role=User.Role.CANDIDATE, telegram_id=None)
    application = ApplicationFactory(vacancy=VacancyFactory(company=company, created_by=hr_user), candidate=candidate)

    message = send_candidate_message(sender=hr_user, application=application, content="Please check your inbox.")

    assert message.delivery_channel == Message.DeliveryChannel.WEB
    assert message.delivery_status == Message.DeliveryStatus.DELIVERED
    assert message.delivered_at is not None
    notification = Notification.objects.get(user=candidate, type=Notification.Type.DIRECT_MESSAGE)
    assert notification.data["message_id"] == str(message.id)
    assert notification.data["delivery_status"] == Message.DeliveryStatus.DELIVERED


def test_accountless_application_is_rejected_without_creating_message():
    hr_user, company = _hr_user_with_company()
    application = ApplicationFactory(vacancy=VacancyFactory(company=company, created_by=hr_user), candidate=None)

    with pytest.raises(ApplicationError) as exc:
        send_candidate_message(sender=hr_user, application=application, content="Hello")

    assert exc.value.message == NO_PLATFORM_INBOX_MESSAGE
    assert Message.objects.count() == 0


def test_telegram_send_failure_keeps_message_with_failed_delivery_metadata():
    hr_user, company = _hr_user_with_company()
    candidate = UserFactory(company=None, role=User.Role.CANDIDATE, telegram_id=112233)
    application = ApplicationFactory(vacancy=VacancyFactory(company=company, created_by=hr_user), candidate=candidate)

    with patch("apps.integrations.telegram_bot.client.requests.post") as post_mock:
        post_mock.return_value.json.return_value = {"ok": False, "description": "Forbidden"}
        message = send_candidate_message(sender=hr_user, application=application, content="Hello")

    message.refresh_from_db()
    assert message.delivery_status == Message.DeliveryStatus.FAILED
    assert message.delivery_failure_reason == "Forbidden"
    assert Notification.objects.get(user=candidate).data["delivery_status"] == Message.DeliveryStatus.FAILED


def test_hr_message_api_rejects_accountless_candidate_with_clear_400():
    hr_user, company = _hr_user_with_company()
    application = ApplicationFactory(vacancy=VacancyFactory(company=company, created_by=hr_user), candidate=None)
    factory = APIRequestFactory()
    request = factory.post(
        f"/api/hr/candidates/{application.id}/messages/",
        {"content": "Hello"},
        format="json",
    )
    force_authenticate(request, user=hr_user)

    response = HRMessageListApi.as_view()(request, application_id=str(application.id))

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["detail"] == NO_PLATFORM_INBOX_MESSAGE
    assert Message.objects.count() == 0


def test_hr_message_api_response_includes_delivery_status():
    hr_user, company = _hr_user_with_company()
    candidate = UserFactory(company=None, role=User.Role.CANDIDATE)
    application = ApplicationFactory(vacancy=VacancyFactory(company=company, created_by=hr_user), candidate=candidate)
    factory = APIRequestFactory()
    request = factory.post(
        f"/api/hr/candidates/{application.id}/messages/",
        {"content": "Hello"},
        format="json",
    )
    force_authenticate(request, user=hr_user)

    response = HRMessageListApi.as_view()(request, application_id=str(application.id))

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["delivery_channel"] == Message.DeliveryChannel.WEB
    assert response.data["delivery_status"] == Message.DeliveryStatus.DELIVERED


def test_hr_message_api_cannot_send_outside_company_scope():
    hr_user, _company = _hr_user_with_company()
    other_company = CompanyFactory()
    other_hr = UserFactory(company=other_company, role=User.Role.HR)
    candidate = UserFactory(company=None, role=User.Role.CANDIDATE)
    application = ApplicationFactory(vacancy=VacancyFactory(company=other_company, created_by=other_hr), candidate=candidate)
    factory = APIRequestFactory()
    request = factory.post(
        f"/api/hr/candidates/{application.id}/messages/",
        {"content": "Hello"},
        format="json",
    )
    force_authenticate(request, user=hr_user)

    response = HRMessageListApi.as_view()(request, application_id=str(application.id))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert Message.objects.count() == 0
