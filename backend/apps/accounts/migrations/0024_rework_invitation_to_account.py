from django.db import migrations, models


def backfill_invitation_account(apps, schema_editor):
    """Move each Invitation from its single company FK to the new account_owner + companies M2M.

    account_owner is derived from invited_by (the HR who sent the invite). The old
    company FK becomes the first (and only) entry in the new companies M2M.
    """
    Invitation = apps.get_model("accounts", "Invitation")
    for inv in Invitation.objects.all().iterator():
        inv.account_owner_id = inv.invited_by_id
        inv.save(update_fields=["account_owner"])
        if inv.company_id:
            inv.companies.add(inv.company_id)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("accounts", "0023_add_account_owner_to_company"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="invitation",
            name="unique_pending_invitation_per_company",
        ),
        migrations.AddField(
            model_name="invitation",
            name="account_owner",
            field=models.ForeignKey(
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name="received_account_invitations",
                to="accounts.user",
            ),
        ),
        migrations.AddField(
            model_name="invitation",
            name="companies",
            field=models.ManyToManyField(
                blank=True,
                related_name="invitations",
                to="accounts.company",
            ),
        ),
        migrations.RunPython(backfill_invitation_account, noop_reverse),
        migrations.AlterField(
            model_name="invitation",
            name="account_owner",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                related_name="received_account_invitations",
                to="accounts.user",
            ),
        ),
        migrations.RemoveField(
            model_name="invitation",
            name="company",
        ),
        migrations.AddConstraint(
            model_name="invitation",
            constraint=models.UniqueConstraint(
                condition=models.Q(is_accepted=False),
                fields=("account_owner", "email"),
                name="unique_pending_invitation_per_account",
            ),
        ),
    ]
