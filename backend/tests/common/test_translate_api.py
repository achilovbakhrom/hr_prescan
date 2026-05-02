from unittest.mock import patch

from rest_framework.test import APIClient

from apps.vacancies.models import Vacancy


def test_public_translate_allows_anonymous_public_vacancy_content(vacancy):
    with patch("apps.common.apis_translate.translate_ai_content", return_value="Описание") as translate:
        response = APIClient().post(
            "/api/translate/",
            {
                "model": "vacancy",
                "object_id": str(vacancy.id),
                "field": "description",
                "target_language": "ru",
            },
            format="json",
        )

    assert response.status_code == 200
    assert response.data == {"translated_text": "Описание", "language": "ru"}
    assert translate.call_args.kwargs["user"].is_anonymous


def test_public_translate_allows_private_vacancy_with_share_token(vacancy):
    vacancy.visibility = Vacancy.Visibility.PRIVATE
    vacancy.save(update_fields=["visibility"])

    with patch("apps.common.apis_translate.translate_ai_content", return_value="Описание"):
        response = APIClient().post(
            "/api/translate/",
            {
                "model": "vacancy",
                "object_id": str(vacancy.id),
                "field": "description",
                "target_language": "ru",
                "share_token": str(vacancy.share_token),
            },
            format="json",
        )

    assert response.status_code == 200


def test_public_translate_rejects_private_vacancy_without_share_token(vacancy):
    vacancy.visibility = Vacancy.Visibility.PRIVATE
    vacancy.save(update_fields=["visibility"])

    with patch("apps.common.apis_translate.translate_ai_content") as translate:
        response = APIClient().post(
            "/api/translate/",
            {
                "model": "vacancy",
                "object_id": str(vacancy.id),
                "field": "description",
                "target_language": "ru",
            },
            format="json",
        )

    assert response.status_code == 403
    translate.assert_not_called()


def test_public_translate_rejects_private_fields(vacancy):
    response = APIClient().post(
        "/api/translate/",
        {
            "model": "interview",
            "object_id": str(vacancy.id),
            "field": "ai_summary",
            "target_language": "ru",
        },
        format="json",
    )

    assert response.status_code == 403
