from django.db import migrations


def seed_industries(apps, schema_editor):
    Industry = apps.get_model("common", "Industry")
    industries = [
        ("accounting", "Accounting"),
        ("advertising", "Advertising & Marketing"),
        ("aerospace", "Aerospace & Defense"),
        ("agriculture", "Agriculture"),
        ("architecture", "Architecture & Planning"),
        ("automotive", "Automotive"),
        ("banking", "Banking"),
        ("biotechnology", "Biotechnology"),
        ("chemicals", "Chemicals"),
        ("construction", "Construction"),
        ("consulting", "Consulting"),
        ("consumer-goods", "Consumer Goods"),
        ("design", "Design"),
        ("ecommerce", "E-Commerce"),
        ("education", "Education"),
        ("electronics", "Electronics"),
        ("energy", "Energy & Utilities"),
        ("engineering", "Engineering"),
        ("entertainment", "Entertainment"),
        ("environmental", "Environmental Services"),
        ("fashion", "Fashion & Apparel"),
        ("finance", "Financial Services"),
        ("food-beverage", "Food & Beverage"),
        ("gaming", "Gaming"),
        ("government", "Government & Public Sector"),
        ("healthcare", "Healthcare"),
        ("hospitality", "Hospitality & Tourism"),
        ("human-resources", "Human Resources"),
        ("insurance", "Insurance"),
        ("internet", "Internet & Web Services"),
        ("it-services", "IT Services"),
        ("legal", "Legal"),
        ("logistics", "Logistics & Supply Chain"),
        ("manufacturing", "Manufacturing"),
        ("media", "Media & Publishing"),
        ("mining", "Mining & Metals"),
        ("music", "Music"),
        ("nonprofit", "Nonprofit & NGO"),
        ("oil-gas", "Oil & Gas"),
        ("pharmaceuticals", "Pharmaceuticals"),
        ("real-estate", "Real Estate"),
        ("retail", "Retail"),
        ("security", "Security"),
        ("semiconductors", "Semiconductors"),
        ("software", "Software & SaaS"),
        ("sports", "Sports & Fitness"),
        ("staffing", "Staffing & Recruiting"),
        ("telecommunications", "Telecommunications"),
        ("textiles", "Textiles"),
        ("transportation", "Transportation"),
        ("venture-capital", "Venture Capital & Private Equity"),
        ("veterinary", "Veterinary"),
        ("warehousing", "Warehousing"),
        ("wellness", "Wellness & Fitness"),
        ("other", "Other"),
    ]
    Industry.objects.bulk_create(
        [Industry(slug=slug, name=name) for slug, name in industries],
        ignore_conflicts=True,
    )


def reverse_seed(apps, schema_editor):
    Industry = apps.get_model("common", "Industry")
    Industry.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0003_create_industry"),
    ]

    operations = [
        migrations.RunPython(seed_industries, reverse_seed),
    ]
