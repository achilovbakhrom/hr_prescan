from django.db import migrations


# (slug, name_ru, name_uz) for all industries
INDUSTRY_TRANSLATIONS = [
    ("accounting", "Бухгалтерия", "Buxgalteriya"),
    ("advertising", "Реклама и маркетинг", "Reklama va marketing"),
    ("aerospace", "Аэрокосмическая отрасль", "Aerokosmik sanoat"),
    ("agriculture", "Сельское хозяйство", "Qishloq xoʻjaligi"),
    ("architecture", "Архитектура и планирование", "Arxitektura va rejalashtirish"),
    ("automotive", "Автомобильная отрасль", "Avtomobil sanoati"),
    ("banking", "Банковское дело", "Bank ishi"),
    ("biotechnology", "Биотехнологии", "Biotexnologiya"),
    ("chemicals", "Химическая промышленность", "Kimyo sanoati"),
    ("construction", "Строительство", "Qurilish"),
    ("consulting", "Консалтинг", "Konsalting"),
    ("consumer-goods", "Товары народного потребления", "Isteʻmol tovarlari"),
    ("design", "Дизайн", "Dizayn"),
    ("ecommerce", "Электронная коммерция", "Elektron tijorat"),
    ("education", "Образование", "Taʻlim"),
    ("electronics", "Электроника", "Elektronika"),
    ("energy", "Энергетика", "Energetika"),
    ("engineering", "Инженерия", "Muhandislik"),
    ("entertainment", "Развлечения", "Koʻngilochar"),
    ("environmental", "Экология", "Ekologiya"),
    ("fashion", "Мода и одежда", "Moda va kiyim-kechak"),
    ("finance", "Финансовые услуги", "Moliya xizmatlari"),
    ("food-beverage", "Продукты питания и напитки", "Oziq-ovqat va ichimliklar"),
    ("gaming", "Игровая индустрия", "Oʻyin sanoati"),
    ("government", "Государственное управление", "Davlat boshqaruvi"),
    ("healthcare", "Здравоохранение", "Sogʻliqni saqlash"),
    ("hospitality", "Гостиничное дело и туризм", "Mehmonxona va turizm"),
    ("human-resources", "Управление персоналом", "Kadrlar boshqaruvi"),
    ("insurance", "Страхование", "Sugʻurta"),
    ("internet", "Интернет и веб-сервисы", "Internet va veb-xizmatlar"),
    ("it-services", "ИТ-услуги", "IT xizmatlari"),
    ("legal", "Юриспруденция", "Yuridik xizmatlar"),
    ("logistics", "Логистика и цепочки поставок", "Logistika va yetkazib berish"),
    ("manufacturing", "Производство", "Ishlab chiqarish"),
    ("media", "СМИ и издательство", "OAV va nashriyot"),
    ("mining", "Добыча полезных ископаемых", "Konchilik"),
    ("music", "Музыка", "Musiqa"),
    ("nonprofit", "Некоммерческий сектор", "Notijorat sektor"),
    ("oil-gas", "Нефть и газ", "Neft va gaz"),
    ("pharmaceuticals", "Фармацевтика", "Farmatsevtika"),
    ("real-estate", "Недвижимость", "Koʻchmas mulk"),
    ("retail", "Розничная торговля", "Chakana savdo"),
    ("security", "Безопасность", "Xavfsizlik"),
    ("semiconductors", "Полупроводники", "Yarim oʻtkazgichlar"),
    ("software", "Программное обеспечение", "Dasturiy taʻminot"),
    ("sports", "Спорт и фитнес", "Sport va fitnes"),
    ("staffing", "Подбор персонала", "Kadrlar tanlash"),
    ("telecommunications", "Телекоммуникации", "Telekommunikatsiya"),
    ("textiles", "Текстильная промышленность", "Toʻqimachilik"),
    ("transportation", "Транспорт", "Transport"),
    ("venture-capital", "Венчурный капитал", "Venchur kapitali"),
    ("veterinary", "Ветеринария", "Veterinariya"),
    ("warehousing", "Складское хозяйство", "Ombor xoʻjaligi"),
    ("wellness", "Велнес и фитнес", "Salomatlik va fitnes"),
    ("other", "Другое", "Boshqa"),
]


def seed_translations(apps, schema_editor):
    Industry = apps.get_model("common", "Industry")
    translations = {slug: (ru, uz) for slug, ru, uz in INDUSTRY_TRANSLATIONS}
    industries = Industry.objects.all()
    to_update = []
    for industry in industries:
        if industry.slug in translations:
            industry.name_ru, industry.name_uz = translations[industry.slug]
            to_update.append(industry)
    Industry.objects.bulk_update(to_update, ["name_ru", "name_uz"])


def reverse_translations(apps, schema_editor):
    Industry = apps.get_model("common", "Industry")
    Industry.objects.all().update(name_ru="", name_uz="")


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0010_seed_country_translations"),
    ]

    operations = [
        migrations.RunPython(seed_translations, reverse_translations),
    ]
