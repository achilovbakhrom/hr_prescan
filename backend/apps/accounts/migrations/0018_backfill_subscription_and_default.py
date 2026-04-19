from django.db import migrations


def forwards(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    CompanyMembership = apps.get_model("accounts", "CompanyMembership")
    db_alias = schema_editor.connection.alias

    # 1. Copy subscription state from Company to User for every HR/admin user tied to a company.
    users_with_company = User.objects.using(db_alias).filter(company__isnull=False).select_related("company")
    for user in users_with_company.iterator():
        company = user.company
        user.subscription_plan_id = company.subscription_plan_id
        user.subscription_status = company.subscription_status
        user.trial_ends_at = company.trial_ends_at
        user.save(update_fields=["subscription_plan", "subscription_status", "trial_ends_at"])

    # 2. Mark the user's membership for their active company as default.
    #    Users without an active company (candidates) get no default — correct by construction.
    for user in users_with_company.iterator():
        (CompanyMembership.objects.using(db_alias).filter(user=user, company=user.company).update(is_default=True))


def backwards(apps, schema_editor):
    CompanyMembership = apps.get_model("accounts", "CompanyMembership")
    db_alias = schema_editor.connection.alias
    CompanyMembership.objects.using(db_alias).update(is_default=False)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0017_add_is_default_to_company_membership"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
