from rest_framework import serializers

from apps.accounts.models import Company, Invitation, User
from apps.accounts.permissions import HRPermissions
from apps.common.country_display import resolve_country_display_name


class CompanyOutputSerializer(serializers.ModelSerializer):
    industries = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="slug",
    )
    country = serializers.SerializerMethodField()

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
            "is_deleted",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_country(self, obj: Company) -> str:
        return resolve_country_display_name(obj.country)


class UserOutputSerializer(serializers.ModelSerializer):
    company = CompanyOutputSerializer(read_only=True)
    full_name = serializers.CharField(read_only=True)
    account_owner_name = serializers.SerializerMethodField()
    is_account_owner = serializers.SerializerMethodField()

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
            "account_owner_name",
            "is_account_owner",
            "hr_permissions",
            "is_active",
            "email_verified",
            "onboarding_completed",
            "subscription_status",
            "trial_ends_at",
            "language",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_account_owner_name(self, obj: User) -> str:
        owner = obj.effective_account_owner
        return owner.full_name or owner.email

    def get_is_account_owner(self, obj: User) -> bool:
        return obj.account_owner_id is None


class InviteHRInputSerializer(serializers.Serializer):
    email = serializers.EmailField()
    permissions = serializers.ListField(
        child=serializers.ChoiceField(choices=HRPermissions.ALL),
        required=False,
        default=list,
    )
    # Companies to grant access to. Omit/empty ⇒ all non-deleted companies on the
    # inviter's account at the time of invite.
    company_ids = serializers.ListField(
        child=serializers.UUIDField(),
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
    companies = CompanyOutputSerializer(many=True, read_only=True)

    class Meta:
        model = Invitation
        fields = [
            "id",
            "email",
            "invited_by_email",
            "companies",
            "permissions",
            "token",
            "is_accepted",
            "expires_at",
            "created_at",
        ]
        read_only_fields = fields


class PendingInvitationOutputSerializer(serializers.ModelSerializer):
    companies = CompanyOutputSerializer(many=True, read_only=True)
    invited_by_name = serializers.SerializerMethodField()
    account_owner_name = serializers.SerializerMethodField()

    class Meta:
        model = Invitation
        fields = [
            "id",
            "companies",
            "invited_by_name",
            "account_owner_name",
            "token",
            "expires_at",
            "created_at",
        ]
        read_only_fields = fields

    def get_invited_by_name(self, obj: Invitation) -> str:
        return obj.invited_by.full_name if obj.invited_by else ""

    def get_account_owner_name(self, obj: Invitation) -> str:
        return obj.account_owner.full_name if obj.account_owner else ""


class TeamMemberUpdateSerializer(serializers.Serializer):
    is_active = serializers.BooleanField(required=False)
    hr_permissions = serializers.ListField(
        child=serializers.ChoiceField(choices=HRPermissions.ALL),
        required=False,
    )
