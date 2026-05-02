import json
from types import SimpleNamespace
from unittest.mock import patch

from rest_framework.test import APIClient

from apps.common.services_translation.translate_vacancy import _parse_translated_items, batch_translate_vacancy_items
from apps.vacancies.models import ScreeningStep, Vacancy


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


def test_batch_translate_persists_wrapped_json_items(vacancy, hr_user):
    criteria = list(vacancy.criteria.filter(step=ScreeningStep.PRESCANNING).order_by("order"))
    payload = {
        "items": [
            {"id": str(criterion.id), "text": f"Критерий {index}"}
            for index, criterion in enumerate(criteria, start=1)
        ]
    }

    with patch("apps.common.services_translation.translate_vacancy.genai.Client") as client_class:
        client = client_class.return_value
        client.models.generate_content.return_value = SimpleNamespace(text=json.dumps(payload), parsed=None)

        results = batch_translate_vacancy_items(
            item_type="criteria",
            vacancy_id=vacancy.id,
            step=ScreeningStep.PRESCANNING,
            target_language="ru",
            user=hr_user,
        )

    assert len(results) == len(criteria)
    criteria[0].refresh_from_db()
    assert criteria[0].translations["ru"] == "Критерий 1"
    assert client.models.generate_content.call_args.kwargs["config"].response_schema is not None


def test_parse_translated_items_accepts_fenced_json_array():
    response = SimpleNamespace(text='```json\n[{"id": "item-1", "text": "Translated"}]\n```', parsed=None)

    assert _parse_translated_items(response) == [{"id": "item-1", "text": "Translated"}]
