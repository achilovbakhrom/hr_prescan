import django.contrib.postgres.indexes
import django.contrib.postgres.search
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vacancies", "0007_enable_pg_trgm"),
    ]

    operations = [
        migrations.AddField(
            model_name="vacancy",
            name="keywords",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name="vacancy",
            name="search_vector",
            field=django.contrib.postgres.search.SearchVectorField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name="vacancy",
            index=django.contrib.postgres.indexes.GinIndex(fields=["search_vector"], name="vacancy_search_vector_gin"),
        ),
    ]
