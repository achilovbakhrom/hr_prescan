from django.db import migrations, models


def backfill_company_account_owner(apps, schema_editor):
    """Set each Company's account_owner from its first ADMIN membership (by created_at).

    Fallbacks for orphan companies (no memberships): first superuser, then oldest user.
    Orphan companies without any user at all are deleted — they're unreachable.
    """
    Company = apps.get_model("accounts", "Company")
    CompanyMembership = apps.get_model("accounts", "CompanyMembership")
    User = apps.get_model("accounts", "User")

    fallback_user = (
        User.objects.filter(is_superuser=True).order_by("created_at").first()
        or User.objects.order_by("created_at").first()
    )

    for company in Company.objects.all().iterator():
        admin = CompanyMembership.objects.filter(company=company, role="admin").order_by("created_at").first()
        if admin is None:
            admin = CompanyMembership.objects.filter(company=company).order_by("created_at").first()
        if admin is not None:
            company.account_owner_id = admin.user_id
            company.save(update_fields=["account_owner"])
            continue
        if fallback_user is None:
            company.delete()
            continue
        company.account_owner_id = fallback_user.id
        company.save(update_fields=["account_owner"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("accounts", "0022_add_account_owner_to_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="account_owner",
            field=models.ForeignKey(
                null=True,
                on_delete=models.deletion.CASCADE,
                related_name="owned_companies",
                to="accounts.user",
            ),
        ),
        migrations.RunPython(backfill_company_account_owner, noop_reverse),
        migrations.AlterField(
            model_name="company",
            name="account_owner",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                related_name="owned_companies",
                to="accounts.user",
            ),
        ),
    ]
