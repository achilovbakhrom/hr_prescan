from rest_framework import serializers

from apps.accounts.models import Company, Invitation, User
from apps.accounts.permissions import HRPermissions


class CompanyOutputSerializer(serializers.ModelSerializer):
    industries = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="slug",
    )

    class Meta:
        model = Company
        fields = [
            "id",
            "name",
            "industries",
            "size",
            "country",
            "logo",
            "website",
            "description",
            "custom_industry",
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
            "hr_permissions",
            "is_active",
            "email_verified",
            "onboarding_completed",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CompanyProfileInputSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    industries = serializers.ListField(
        child=serializers.SlugField(max_length=50),
        required=False,
    )
    size = serializers.ChoiceField(choices=Company.Size.choices, required=False)
    country = serializers.CharField(max_length=100, required=False)
    website = serializers.URLField(max_length=500, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    logo = serializers.CharField(max_length=500, required=False, allow_blank=True)
    custom_industry = serializers.CharField(max_length=255, required=False, allow_blank=True)


class InviteHRInputSerializer(serializers.Serializer):
    email = serializers.EmailField()
    permissions = serializers.ListField(
        child=serializers.ChoiceField(choices=HRPermissions.ALL),
        required=False,
        default=list,
    )


class AcceptInvitationInputSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField(min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)


class InvitationOutputSerializer(serializers.ModelSerializer):
    invited_by_email = serializers.EmailField(source="invited_by.email", read_only=True)

    class Meta:
        model = Invitation
        fields = [
            "id",
            "email",
            "invited_by_email",
            "permissions",
            "token",
            "is_accepted",
            "expires_at",
            "created_at",
        ]
        read_only_fields = fields


class PendingInvitationOutputSerializer(serializers.ModelSerializer):
    company = CompanyOutputSerializer(read_only=True)
    invited_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Invitation
        fields = [
            "id",
            "company",
            "invited_by_name",
            "token",
            "expires_at",
            "created_at",
        ]
        read_only_fields = fields

    def get_invited_by_name(self, obj: Invitation) -> str:
        return obj.invited_by.full_name if obj.invited_by else ""


class TeamMemberUpdateSerializer(serializers.Serializer):
    is_active = serializers.BooleanField(required=False)
    hr_permissions = serializers.ListField(
        child=serializers.ChoiceField(choices=HRPermissions.ALL),
        required=False,
    )
