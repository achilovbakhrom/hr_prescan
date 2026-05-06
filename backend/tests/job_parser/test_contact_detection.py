from types import SimpleNamespace

from apps.job_parser.services.contact_detection import parsed_vacancy_has_contact_info, text_has_contact_info


def test_text_has_contact_info_for_email_telegram_whatsapp_and_phone():
    assert text_has_contact_info("Send CV to hr@example.com")
    assert text_has_contact_info("Write to @company_hr")
    assert text_has_contact_info("Contact via WhatsApp +998 90 123 45 67")
    assert text_has_contact_info("Tel: 90 123 45 67")


def test_text_has_contact_info_ignores_plain_long_numbers_without_contact_context():
    assert not text_has_contact_info("Salary from 12000000 to 18000000 UZS")


def test_parsed_vacancy_has_contact_info_uses_hh_contacts_payload():
    vacancy = SimpleNamespace(
        description="No visible contacts",
        requirements="",
        responsibilities="",
        raw_payload={"contacts": {"phones": [{"country": "998", "city": "90", "number": "1234567"}]}},
    )

    assert parsed_vacancy_has_contact_info(vacancy)
