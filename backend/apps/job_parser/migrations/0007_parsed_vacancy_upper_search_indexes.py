import django.contrib.postgres.indexes
import django.db.models.functions.text
from django.contrib.postgres.operations import AddIndexConcurrently, RemoveIndexConcurrently
from django.db import migrations


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("job_parser", "0006_parsed_vacancy_search_indexes"),
    ]

    operations = [
        RemoveIndexConcurrently(model_name="parsedvacancy", name="parsed_vac_title_trgm"),
        RemoveIndexConcurrently(model_name="parsedvacancy", name="parsed_vac_desc_trgm"),
        RemoveIndexConcurrently(model_name="parsedvacancy", name="parsed_vac_req_trgm"),
        RemoveIndexConcurrently(model_name="parsedvacancy", name="parsed_vac_resp_trgm"),
        RemoveIndexConcurrently(model_name="parsedvacancy", name="parsed_vac_company_trgm"),
        RemoveIndexConcurrently(model_name="parsedvacancy", name="parsed_vac_location_trgm"),
        AddIndexConcurrently(
            model_name="parsedvacancy",
            index=django.contrib.postgres.indexes.GinIndex(
                django.contrib.postgres.indexes.OpClass(
                    django.db.models.functions.text.Upper("title"),
                    name="gin_trgm_ops",
                ),
                name="parsed_vac_title_trgm",
            ),
        ),
        AddIndexConcurrently(
            model_name="parsedvacancy",
            index=django.contrib.postgres.indexes.GinIndex(
                django.contrib.postgres.indexes.OpClass(
                    django.db.models.functions.text.Upper("description"),
                    name="gin_trgm_ops",
                ),
                name="parsed_vac_desc_trgm",
            ),
        ),
        AddIndexConcurrently(
            model_name="parsedvacancy",
            index=django.contrib.postgres.indexes.GinIndex(
                django.contrib.postgres.indexes.OpClass(
                    django.db.models.functions.text.Upper("requirements"),
                    name="gin_trgm_ops",
                ),
                name="parsed_vac_req_trgm",
            ),
        ),
        AddIndexConcurrently(
            model_name="parsedvacancy",
            index=django.contrib.postgres.indexes.GinIndex(
                django.contrib.postgres.indexes.OpClass(
                    django.db.models.functions.text.Upper("responsibilities"),
                    name="gin_trgm_ops",
                ),
                name="parsed_vac_resp_trgm",
            ),
        ),
        AddIndexConcurrently(
            model_name="parsedvacancy",
            index=django.contrib.postgres.indexes.GinIndex(
                django.contrib.postgres.indexes.OpClass(
                    django.db.models.functions.text.Upper("company_name"),
                    name="gin_trgm_ops",
                ),
                name="parsed_vac_company_trgm",
            ),
        ),
        AddIndexConcurrently(
            model_name="parsedvacancy",
            index=django.contrib.postgres.indexes.GinIndex(
                django.contrib.postgres.indexes.OpClass(
                    django.db.models.functions.text.Upper("location"),
                    name="gin_trgm_ops",
                ),
                name="parsed_vac_location_trgm",
            ),
        ),
    ]
