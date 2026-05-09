import django.contrib.postgres.indexes
from django.contrib.postgres.operations import AddIndexConcurrently
from django.db import migrations


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("job_parser", "0005_parsedvacancy_has_contact_info"),
    ]

    operations = [
        AddIndexConcurrently(
            model_name="parsedvacancy",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["title"],
                name="parsed_vac_title_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
        AddIndexConcurrently(
            model_name="parsedvacancy",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["description"],
                name="parsed_vac_desc_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
        AddIndexConcurrently(
            model_name="parsedvacancy",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["requirements"],
                name="parsed_vac_req_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
        AddIndexConcurrently(
            model_name="parsedvacancy",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["responsibilities"],
                name="parsed_vac_resp_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
        AddIndexConcurrently(
            model_name="parsedvacancy",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["company_name"],
                name="parsed_vac_company_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
        AddIndexConcurrently(
            model_name="parsedvacancy",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["location"],
                name="parsed_vac_location_trgm",
                opclasses=["gin_trgm_ops"],
            ),
        ),
    ]
