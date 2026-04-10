from django.db import migrations


TRANSLATIONS = {
    'ar': ('Арабский', 'Arab'),
    'az': ('Азербайджанский', 'Ozarbayjon'),
    'be': ('Белорусский', 'Belarus'),
    'bg': ('Болгарский', 'Bolgar'),
    'bn': ('Бенгальский', 'Bengal'),
    'bs': ('Боснийский', 'Bosniya'),
    'ca': ('Каталанский', 'Katalan'),
    'cs': ('Чешский', 'Chex'),
    'da': ('Датский', 'Dan'),
    'de': ('Немецкий', 'Nemis'),
    'el': ('Греческий', 'Grek'),
    'en': ('Английский', 'Ingliz'),
    'es': ('Испанский', 'Ispan'),
    'et': ('Эстонский', 'Estoniya'),
    'fa': ('Персидский', 'Fors'),
    'fi': ('Финский', 'Fin'),
    'fr': ('Французский', 'Fransuz'),
    'he': ('Иврит', 'Ibroniy'),
    'hi': ('Хинди', 'Xind'),
    'hr': ('Хорватский', 'Xorvat'),
    'hu': ('Венгерский', 'Venger'),
    'hy': ('Армянский', 'Arman'),
    'id': ('Индонезийский', 'Indonez'),
    'it': ('Итальянский', 'Italyan'),
    'ja': ('Японский', 'Yapon'),
    'ka': ('Грузинский', 'Gruzin'),
    'kk': ('Казахский', 'Qozoq'),
    'ko': ('Корейский', 'Koreys'),
    'ky': ('Киргизский', "Qirg'iz"),
    'lt': ('Литовский', 'Litva'),
    'lv': ('Латышский', 'Latish'),
    'mk': ('Македонский', 'Makedon'),
    'mn': ('Монгольский', "Mo'g'ul"),
    'ms': ('Малайский', 'Malay'),
    'nl': ('Нидерландский', 'Golland'),
    'no': ('Норвежский', 'Norveg'),
    'pl': ('Польский', 'Polyak'),
    'pt': ('Португальский', 'Portugal'),
    'ro': ('Румынский', 'Rumin'),
    'ru': ('Русский', 'Rus'),
    'sk': ('Словацкий', 'Slovak'),
    'sl': ('Словенский', 'Sloven'),
    'sq': ('Албанский', 'Alban'),
    'sr': ('Сербский', 'Serb'),
    'sv': ('Шведский', 'Shved'),
    'sw': ('Суахили', 'Suahili'),
    'tg': ('Таджикский', 'Tojik'),
    'th': ('Тайский', 'Tay'),
    'tk': ('Туркменский', 'Turkman'),
    'tr': ('Турецкий', 'Turk'),
    'uk': ('Украинский', 'Ukrain'),
    'ur': ('Урду', 'Urdu'),
    'uz': ('Узбекский', "O'zbek"),
    'vi': ('Вьетнамский', 'Vyetnam'),
    'zh': ('Китайский', 'Xitoy'),
}


def seed_translations(apps, schema_editor):
    Language = apps.get_model('common', 'Language')
    for code, (name_ru, name_uz) in TRANSLATIONS.items():
        Language.objects.filter(code=code).update(name_ru=name_ru, name_uz=name_uz)


def reverse(apps, schema_editor):
    Language = apps.get_model('common', 'Language')
    Language.objects.filter(code__in=TRANSLATIONS.keys()).update(name_ru='', name_uz='')


class Migration(migrations.Migration):
    dependencies = [
        ('common', '0012_add_language_translations'),
    ]
    operations = [
        migrations.RunPython(seed_translations, reverse),
    ]
