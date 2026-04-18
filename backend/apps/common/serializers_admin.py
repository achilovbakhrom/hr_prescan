from rest_framework import serializers

from apps.accounts.models import User


class AdminCompanyListOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    industry = serializers.CharField()
    size = serializers.CharField()
    country = serializers.CharField()
    user_count = serializers.IntegerField()
    vacancy_count = serializers.IntegerField()
    is_deleted = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class AdminCompanyDetailOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    industry = serializers.CharField()
    size = serializers.CharField()
    country = serializers.CharField()
    website = serializers.URLField(allow_null=True)
    description = serializers.CharField(allow_null=True)
    is_deleted = serializers.BooleanField()
    deleted_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class AdminCompanyUpdateInputSerializer(serializers.Serializer):
    is_deleted = serializers.BooleanField(required=False)


class AdminUserListOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    role = serializers.CharField()
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField()
    subscription_status = serializers.CharField()
    company_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()

    def get_company_name(self, obj: User) -> str | None:
        return obj.company.name if obj.company else None


class AdminUserDetailOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField(allow_null=True)
    role = serializers.CharField()
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField()
    email_verified = serializers.BooleanField()
    subscription_status = serializers.CharField()
    trial_ends_at = serializers.DateTimeField(allow_null=True)
    company_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()

    def get_company_name(self, obj: User) -> str | None:
        return obj.company.name if obj.company else None


class AdminUserUpdateInputSerializer(serializers.Serializer):
    is_active = serializers.BooleanField(required=False)
    is_staff = serializers.BooleanField(required=False)
    subscription_status = serializers.ChoiceField(
        choices=User.SubscriptionStatus.choices,
        required=False,
    )
