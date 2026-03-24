from rest_framework import serializers

from apps.accounts.models import Company, Invitation, User


class CompanyOutputSerializer(serializers.ModelSerializer):
    industries = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="slug",
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
            "onboarding_completed",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class CompanyRegisterInputSerializer(serializers.Serializer):
    # Company fields
    company_name = serializers.CharField(max_length=255)
    industries = serializers.ListField(
        child=serializers.SlugField(max_length=50),
        required=False, default=list,
    )
    size = serializers.ChoiceField(choices=Company.Size.choices)
    country = serializers.CharField(max_length=100)
    website = serializers.URLField(max_length=500, required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)

    # Admin user fields
    admin_email = serializers.EmailField()
    admin_password = serializers.CharField(min_length=8)
    admin_first_name = serializers.CharField(max_length=150)
    admin_last_name = serializers.CharField(max_length=150)


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


class InviteHRInputSerializer(serializers.Serializer):
    email = serializers.EmailField()


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
    is_active = serializers.BooleanField()
