import apps.accounts.models
import django.db.models.deletion
import uuid

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Invitation",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("email", models.EmailField(max_length=254)),
                ("token", models.UUIDField(default=uuid.uuid4, unique=True)),
                ("is_accepted", models.BooleanField(default=False)),
                (
                    "expires_at",
                    models.DateTimeField(
                        default=apps.accounts.models._default_invitation_expiry,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="invitations",
                        to="accounts.company",
                    ),
                ),
                (
                    "invited_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sent_invitations",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="invitation",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_accepted", False)),
                fields=("company", "email"),
                name="unique_pending_invitation_per_company",
            ),
        ),
    ]
