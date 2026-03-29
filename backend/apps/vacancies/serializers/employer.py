from rest_framework import serializers

from apps.vacancies.models import EmployerCompany


class EmployerCompanyOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerCompany
        fields = [
            "id",
            "name",
            "industry",
            "logo",
            "website",
            "description",
            "description_translations",
            "source",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
