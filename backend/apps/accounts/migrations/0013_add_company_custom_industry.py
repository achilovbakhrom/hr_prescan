from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0012_add_company_membership"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="custom_industry",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
    ]
