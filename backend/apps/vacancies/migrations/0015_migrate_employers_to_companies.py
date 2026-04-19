from django.db import migrations


def forwards(apps, schema_editor):
    """Create a standalone Company (+ membership) per EmployerCompany and repoint vacancies.

    EmployerCompany was a child of a tenant Company. In the new model every Company
    stands on its own, owned by users via CompanyMembership. For each EmployerCompany E
    under parent C:
      1. Build a new Company row mirroring E's user-facing fields, seeded with C's size
         and country (E doesn't carry those).
      2. Give the parent's admin (or any ADMIN/HR member if no admin exists) a membership
         to the new company with is_default=False — they already have a default from PR 1.
      3. Record E.migrated_company_id so 0016 can reassign Vacancy.company.
    """
    EmployerCompany = apps.get_model("vacancies", "EmployerCompany")
    Company = apps.get_model("accounts", "Company")
    CompanyMembership = apps.get_model("accounts", "CompanyMembership")
    Vacancy = apps.get_model("vacancies", "Vacancy")
    db_alias = schema_editor.connection.alias

    for employer in EmployerCompany.objects.using(db_alias).select_related("company").iterator():
        parent = employer.company

        admin_membership = (
            CompanyMembership.objects.using(db_alias)
            .filter(company=parent, role="admin")
            .order_by("created_at")
            .first()
        )
        if admin_membership is None:
            admin_membership = (
                CompanyMembership.objects.using(db_alias).filter(company=parent).order_by("created_at").first()
            )
        if admin_membership is None:
            # Parent has no memberships at all — skip. The underlying vacancies still
            # reference the parent Company (the old Vacancy.company), which is a valid
            # row in the new model too.
            continue

        new_company = Company.objects.using(db_alias).create(
            name=employer.name,
            custom_industry=employer.industry or "",
            size=parent.size,
            country=parent.country,
            website=employer.website or "",
            description=employer.description or "",
            is_deleted=False,
        )

        CompanyMembership.objects.using(db_alias).create(
            user=admin_membership.user,
            company=new_company,
            role=admin_membership.role,
            hr_permissions=admin_membership.hr_permissions,
            is_default=False,
        )

        employer.migrated_company_id = new_company.id
        employer.save(update_fields=["migrated_company_id"])

    # Repoint vacancies that had an employer. Those with employer=None keep the tenant
    # company they already point at — that's correct under the flat model.
    vacancies_with_employer = Vacancy.objects.using(db_alias).filter(employer__isnull=False)
    for vacancy in vacancies_with_employer.select_related("employer").iterator():
        if vacancy.employer.migrated_company_id is None:
            continue
        vacancy.company_id = vacancy.employer.migrated_company_id
        vacancy.save(update_fields=["company"])


def backwards(apps, schema_editor):
    """Best-effort reverse: reset Vacancy.company back to the EmployerCompany's parent.

    Fully reversing this migration would require preserving the original Vacancy.company
    values, which we didn't. Instead, we walk vacancies whose current company matches a
    migrated-from company and restore them to the employer's parent, then delete the
    generated Company/Membership rows.
    """
    EmployerCompany = apps.get_model("vacancies", "EmployerCompany")
    Company = apps.get_model("accounts", "Company")
    Vacancy = apps.get_model("vacancies", "Vacancy")
    db_alias = schema_editor.connection.alias

    for employer in (
        EmployerCompany.objects.using(db_alias)
        .filter(migrated_company_id__isnull=False)
        .select_related("company")
        .iterator()
    ):
        Vacancy.objects.using(db_alias).filter(
            employer=employer,
            company_id=employer.migrated_company_id,
        ).update(company_id=employer.company_id)

        Company.objects.using(db_alias).filter(id=employer.migrated_company_id).delete()

    EmployerCompany.objects.using(db_alias).update(migrated_company_id=None)


class Migration(migrations.Migration):
    atomic = False  # Iterating and creating Company/Membership rows — avoid one big txn.

    dependencies = [
        ("vacancies", "0014_add_employer_migrated_company_id"),
        ("accounts", "0021_drop_subscription_fields_from_company"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
