from rest_framework import serializers

from apps.accounts.models import Company, User


class CompanyOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "industry",
            "size",
            "country",
            "logo",
            "website",
            "description",
            "subscription_status",
            "trial_ends_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class UserOutputSerializer(serializers.ModelSerializer):
    company = CompanyOutputSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "role",
            "company",
            "is_active",
            "email_verified",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields
