import django.db.models.deletion
from django.db import migrations, models


def forwards_backfill(apps, schema_editor):
    CompanySubscription = apps.get_model("subscriptions", "CompanySubscription")
    CompanyMembership = apps.get_model("accounts", "CompanyMembership")
    db_alias = schema_editor.connection.alias

    orphans = []
    for sub in CompanySubscription.objects.using(db_alias).select_related("company").iterator():
        admin = (
            CompanyMembership.objects.using(db_alias)
            .filter(company=sub.company, role="admin")
            .select_related("user")
            .order_by("created_at")
            .first()
        )
        if admin is None:
            orphans.append(sub.id)
            continue
        sub.user_id = admin.user_id
        sub.save(update_fields=["user"])

    if orphans:
        # Companies without an admin membership cannot anchor a subscription after this migration.
        # Dropping them preserves the one-subscription-per-user invariant we're about to enforce.
        CompanySubscription.objects.using(db_alias).filter(id__in=orphans).delete()


def backwards_backfill(apps, schema_editor):
    # Reverse path: try to re-point at the user's current company. Missing data is expected.
    CompanySubscription = apps.get_model("subscriptions", "CompanySubscription")
    db_alias = schema_editor.connection.alias
    for sub in CompanySubscription.objects.using(db_alias).select_related("user").iterator():
        company_id = getattr(sub.user, "company_id", None)
        if company_id is None:
            continue
        sub.company_id = company_id
        sub.save(update_fields=["company"])


class Migration(migrations.Migration):
    dependencies = [
        ("subscriptions", "0002_seed_default_plans"),
        ("accounts", "0021_drop_subscription_fields_from_company"),
    ]

    operations = [
        migrations.AddField(
            model_name="companysubscription",
            name="user",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="subscription",
                to="accounts.user",
            ),
        ),
        migrations.RunPython(forwards_backfill, backwards_backfill),
        migrations.RemoveField(
            model_name="companysubscription",
            name="company",
        ),
        migrations.AlterField(
            model_name="companysubscription",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="subscription",
                to="accounts.user",
            ),
        ),
        migrations.RenameModel(
            old_name="CompanySubscription",
            new_name="UserSubscription",
        ),
    ]
