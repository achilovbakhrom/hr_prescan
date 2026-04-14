from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone

from apps.accounts.models import Company, User
from apps.accounts.services import (
    accept_invitation,
    accept_invitation_existing_user,
    activate_user,
    create_company_with_admin,
    deactivate_user,
    invite_hr,
    register_user,
    verify_email,
)
from apps.common.exceptions import ApplicationError
from tests.factories import CompanyFactory, UserFactory

# ---------------------------------------------------------------------------
# register_user
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestRegisterUser:
    @patch("apps.accounts.services.send_verification_email")
    def test_register_creates_candidate_user(self, mock_send):
        """register_user creates a user with role=candidate and email_verified=False."""
        user = register_user(
            email="alice@example.com",
            password="StrongPass123!",
            first_name="Alice",
            last_name="Smith",
        )

        assert user.role == User.Role.CANDIDATE
        assert user.email_verified is False
        assert user.email == "alice@example.com"
        assert user.first_name == "Alice"
        assert user.last_name == "Smith"
        assert user.company is None
        mock_send.delay.assert_called_once_with(user_id=str(user.id))

    @patch("apps.accounts.services.send_verification_email")
    def test_register_duplicate_email_fails(self, mock_send):
        """Registering with an existing email raises ApplicationError."""
        UserFactory(email="duplicate@example.com")

        with pytest.raises(ApplicationError, match="already exists"):
            register_user(
                email="duplicate@example.com",
                password="StrongPass123!",
                first_name="Bob",
                last_name="Brown",
            )

    @patch("apps.accounts.services.send_verification_email")
    @patch("apps.applications.services.bind_existing_applications")
    def test_register_binds_existing_applications(self, mock_bind, mock_send):
        """After registration, bind_existing_applications can be called for the user."""
        user = register_user(
            email="candidate@example.com",
            password="StrongPass123!",
            first_name="Cara",
            last_name="Jones",
        )

        # Simulate calling bind after registration (the caller is responsible)
        from apps.applications.services import bind_existing_applications

        bind_existing_applications(user=user)
        mock_bind.assert_called_once_with(user=user)


# ---------------------------------------------------------------------------
# verify_email
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestVerifyEmail:
    def test_verify_email_sets_verified(self):
        """verify_email sets email_verified=True on the user."""
        user = UserFactory(email_verified=False)

        result = verify_email(token=str(user.id))

        result.refresh_from_db()
        assert result.email_verified is True

    def test_verify_email_invalid_token_fails(self):
        """An invalid token raises ApplicationError."""
        with pytest.raises(ApplicationError, match="Invalid or expired"):
            verify_email(token="not-a-valid-uuid")

    def test_verify_email_already_verified_fails(self):
        """Verifying an already-verified email raises ApplicationError."""
        user = UserFactory(email_verified=True)

        with pytest.raises(ApplicationError, match="already verified"):
            verify_email(token=str(user.id))


# ---------------------------------------------------------------------------
# create_company_with_admin
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestCreateCompanyWithAdmin:
    @patch("apps.accounts.services.send_verification_email")
    def test_creates_company_and_admin(self, mock_send):
        """Creates both a Company and an admin User."""
        company, admin = create_company_with_admin(
            company_name="Acme Corp",
            industry="Technology",
            size=Company.Size.SMALL,
            country="Netherlands",
            admin_email="admin@acme.com",
            admin_password="AdminPass123!",
            admin_first_name="Admin",
            admin_last_name="User",
        )

        assert isinstance(company, Company)
        assert company.name == "Acme Corp"
        assert isinstance(admin, User)
        assert admin.role == User.Role.ADMIN
        assert admin.email == "admin@acme.com"
        mock_send.delay.assert_called_once()

    @patch("apps.accounts.services.send_verification_email")
    def test_admin_linked_to_company(self, mock_send):
        """The admin user's company field points to the newly created company."""
        company, admin = create_company_with_admin(
            company_name="Beta Inc",
            industry="Finance",
            size=Company.Size.MEDIUM,
            country="Germany",
            admin_email="admin@beta.com",
            admin_password="AdminPass123!",
            admin_first_name="Beta",
            admin_last_name="Admin",
        )

        assert admin.company_id == company.id
        assert admin.company.name == "Beta Inc"

    @patch("apps.accounts.services.send_verification_email")
    def test_duplicate_admin_email_fails(self, mock_send):
        """Fails if the admin email is already taken."""
        UserFactory(email="taken@example.com")

        with pytest.raises(ApplicationError, match="already exists"):
            create_company_with_admin(
                company_name="Gamma LLC",
                industry="Healthcare",
                size=Company.Size.LARGE,
                country="UK",
                admin_email="taken@example.com",
                admin_password="AdminPass123!",
                admin_first_name="Gamma",
                admin_last_name="Admin",
            )


# ---------------------------------------------------------------------------
# invite_hr
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestInviteHR:
    @patch("apps.accounts.services.send_invitation_email")
    def test_invite_creates_invitation(self, mock_send):
        """Creates an Invitation with correct fields."""
        company = CompanyFactory()
        admin = UserFactory(company=company, role=User.Role.ADMIN)

        invitation = invite_hr(
            company=company,
            email="newhire@example.com",
            invited_by=admin,
        )

        assert invitation.company == company
        assert invitation.email == "newhire@example.com"
        assert invitation.invited_by == admin
        assert invitation.is_accepted is False
        assert invitation.token is not None
        mock_send.delay.assert_called_once_with(invitation_id=str(invitation.id))

    @patch("apps.accounts.services.send_invitation_email")
    def test_invite_duplicate_pending_fails(self, mock_send):
        """Cannot invite the same email twice to the same company while pending."""
        company = CompanyFactory()
        admin = UserFactory(company=company, role=User.Role.ADMIN)

        invite_hr(company=company, email="hr@example.com", invited_by=admin)

        with pytest.raises(ApplicationError, match="already been sent"):
            invite_hr(company=company, email="hr@example.com", invited_by=admin)

    @patch("apps.accounts.services.send_invitation_email")
    def test_invitation_has_expiry(self, mock_send):
        """Invitation expires_at is set to approximately 7 days from now."""
        company = CompanyFactory()
        admin = UserFactory(company=company, role=User.Role.ADMIN)

        before = timezone.now()
        invitation = invite_hr(
            company=company,
            email="future@example.com",
            invited_by=admin,
        )
        after = timezone.now()

        expected_min = before + timedelta(days=7)
        expected_max = after + timedelta(days=7)
        assert expected_min <= invitation.expires_at <= expected_max

    @patch("apps.accounts.services.send_invitation_email")
    def test_invite_existing_user_email_fails(self, mock_send):
        """Cannot invite an email that already belongs to a registered user."""
        company = CompanyFactory()
        admin = UserFactory(company=company, role=User.Role.ADMIN)
        UserFactory(email="existing@example.com")

        with pytest.raises(ApplicationError, match="already exists"):
            invite_hr(company=company, email="existing@example.com", invited_by=admin)


# ---------------------------------------------------------------------------
# accept_invitation
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAcceptInvitation:
    @patch("apps.accounts.services.send_invitation_email")
    def test_accept_creates_hr_user(self, mock_send):
        """Accepting an invitation creates a user with role=hr linked to the company."""
        company = CompanyFactory()
        admin = UserFactory(company=company, role=User.Role.ADMIN)
        invitation = invite_hr(company=company, email="newhr@example.com", invited_by=admin)

        user = accept_invitation(
            token=invitation.token,
            password="HrPass123!",
            first_name="New",
            last_name="HR",
        )

        assert user.role == User.Role.HR
        assert user.company_id == company.id
        assert user.email == "newhr@example.com"

    @patch("apps.accounts.services.send_invitation_email")
    def test_accept_marks_invitation_accepted(self, mock_send):
        """After acceptance, invitation.is_accepted becomes True."""
        company = CompanyFactory()
        admin = UserFactory(company=company, role=User.Role.ADMIN)
        invitation = invite_hr(company=company, email="accept@example.com", invited_by=admin)

        accept_invitation(
            token=invitation.token,
            password="HrPass123!",
            first_name="Accept",
            last_name="Test",
        )

        invitation.refresh_from_db()
        assert invitation.is_accepted is True

    @patch("apps.accounts.services.send_invitation_email")
    def test_accept_expired_invitation_fails(self, mock_send):
        """Accepting an expired invitation raises ApplicationError."""
        company = CompanyFactory()
        admin = UserFactory(company=company, role=User.Role.ADMIN)
        invitation = invite_hr(company=company, email="expired@example.com", invited_by=admin)

        # Force the invitation to be expired
        invitation.expires_at = timezone.now() - timedelta(days=1)
        invitation.save(update_fields=["expires_at"])

        with pytest.raises(ApplicationError, match="expired"):
            accept_invitation(
                token=invitation.token,
                password="HrPass123!",
                first_name="Expired",
                last_name="Test",
            )

    @patch("apps.accounts.services.send_invitation_email")
    def test_accept_already_accepted_fails(self, mock_send):
        """Accepting an already accepted invitation raises ApplicationError."""
        company = CompanyFactory()
        admin = UserFactory(company=company, role=User.Role.ADMIN)
        invitation = invite_hr(company=company, email="double@example.com", invited_by=admin)

        # Accept first time
        accept_invitation(
            token=invitation.token,
            password="HrPass123!",
            first_name="Double",
            last_name="Accept",
        )

        with pytest.raises(ApplicationError, match="already been accepted"):
            accept_invitation(
                token=invitation.token,
                password="AnotherPass123!",
                first_name="Double",
                last_name="Again",
            )


# ---------------------------------------------------------------------------
# accept_invitation_existing_user
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAcceptInvitationExistingUser:
    @patch("apps.accounts.services.send_invitation_email")
    def test_switches_company_and_role(self, mock_send):
        """Existing user gets the invitation's company and role=hr."""
        company = CompanyFactory()
        admin = UserFactory(company=company, role=User.Role.ADMIN)
        existing_user = UserFactory(
            email="switchable@example.com",
            role=User.Role.CANDIDATE,
            company=None,
        )
        invitation = invite_hr(
            company=company,
            email="switchable@example.com",
            invited_by=admin,
        )

        result = accept_invitation_existing_user(
            user=existing_user,
            token=invitation.token,
        )

        result.refresh_from_db()
        assert result.company_id == company.id
        assert result.role == User.Role.HR

    @patch("apps.accounts.services.send_invitation_email")
    def test_accept_existing_marks_invitation_accepted(self, mock_send):
        """Invitation is marked as accepted after existing user accepts."""
        company = CompanyFactory()
        admin = UserFactory(company=company, role=User.Role.ADMIN)
        existing_user = UserFactory(
            email="mark@example.com",
            role=User.Role.CANDIDATE,
            company=None,
        )
        invitation = invite_hr(
            company=company,
            email="mark@example.com",
            invited_by=admin,
        )

        accept_invitation_existing_user(user=existing_user, token=invitation.token)

        invitation.refresh_from_db()
        assert invitation.is_accepted is True

    @patch("apps.accounts.services.send_invitation_email")
    def test_accept_existing_wrong_email_fails(self, mock_send):
        """Fails if the user's email does not match the invitation email."""
        company = CompanyFactory()
        admin = UserFactory(company=company, role=User.Role.ADMIN)
        wrong_user = UserFactory(
            email="wrong@example.com",
            role=User.Role.CANDIDATE,
            company=None,
        )
        invitation = invite_hr(
            company=company,
            email="correct@example.com",
            invited_by=admin,
        )

        with pytest.raises(ApplicationError, match="different email"):
            accept_invitation_existing_user(user=wrong_user, token=invitation.token)


# ---------------------------------------------------------------------------
# activate_user / deactivate_user
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestActivateDeactivateUser:
    def test_deactivate_user(self):
        """deactivate_user sets is_active=False."""
        company = CompanyFactory()
        admin = UserFactory(company=company, role=User.Role.ADMIN)
        hr_user = UserFactory(company=company, role=User.Role.HR, is_active=True)

        result = deactivate_user(user=hr_user, deactivated_by=admin)

        result.refresh_from_db()
        assert result.is_active is False

    def test_activate_user(self):
        """activate_user sets is_active=True."""
        company = CompanyFactory()
        admin = UserFactory(company=company, role=User.Role.ADMIN)
        hr_user = UserFactory(company=company, role=User.Role.HR, is_active=False)

        result = activate_user(user=hr_user, activated_by=admin)

        result.refresh_from_db()
        assert result.is_active is True

    def test_deactivate_non_admin_fails(self):
        """Only admins can deactivate users."""
        company = CompanyFactory()
        hr_actor = UserFactory(company=company, role=User.Role.HR)
        target = UserFactory(company=company, role=User.Role.HR)

        with pytest.raises(ApplicationError, match="Only admins"):
            deactivate_user(user=target, deactivated_by=hr_actor)

    def test_deactivate_cross_company_fails(self):
        """Cannot deactivate a user from a different company."""
        company_a = CompanyFactory()
        company_b = CompanyFactory()
        admin_a = UserFactory(company=company_a, role=User.Role.ADMIN)
        user_b = UserFactory(company=company_b, role=User.Role.HR)

        with pytest.raises(ApplicationError, match="own company"):
            deactivate_user(user=user_b, deactivated_by=admin_a)

    def test_deactivate_self_fails(self):
        """Admin cannot deactivate themselves."""
        company = CompanyFactory()
        admin = UserFactory(company=company, role=User.Role.ADMIN)

        with pytest.raises(ApplicationError, match="cannot deactivate yourself"):
            deactivate_user(user=admin, deactivated_by=admin)

    def test_deactivate_already_inactive_fails(self):
        """Cannot deactivate a user that is already inactive."""
        company = CompanyFactory()
        admin = UserFactory(company=company, role=User.Role.ADMIN)
        hr_user = UserFactory(company=company, role=User.Role.HR, is_active=False)

        with pytest.raises(ApplicationError, match="already deactivated"):
            deactivate_user(user=hr_user, deactivated_by=admin)

    def test_activate_already_active_fails(self):
        """Cannot activate a user that is already active."""
        company = CompanyFactory()
        admin = UserFactory(company=company, role=User.Role.ADMIN)
        hr_user = UserFactory(company=company, role=User.Role.HR, is_active=True)

        with pytest.raises(ApplicationError, match="already active"):
            activate_user(user=hr_user, activated_by=admin)
