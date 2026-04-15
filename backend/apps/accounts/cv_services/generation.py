import uuid

from django.conf import settings
from django.template.loader import render_to_string

from apps.accounts.models import CandidateCV, CandidateProfile


def generate_cv_pdf(*, profile, template_name="classic", cv_name="My CV"):
    """Generate PDF from profile data using WeasyPrint, upload to MinIO, return CandidateCV."""
    from weasyprint import HTML

    from apps.applications.services import _get_s3_client, generate_cv_download_url

    # 1. Prefetch all related data
    profile = (
        CandidateProfile.objects.select_related("user")
        .prefetch_related(
            "skills",
            "work_experiences",
            "educations__education_level",
            "languages__language",
            "certifications",
        )
        .get(pk=profile.pk)
    )

    # 2. Render HTML
    html_string = render_to_string(
        f"cv/{template_name}.html",
        {"profile": profile, "user": profile.user},
    )

    # 3. Convert to PDF
    pdf_bytes = HTML(string=html_string).write_pdf()

    # 4. Upload to MinIO
    file_key = f"cv-generated/{profile.user_id}/{uuid.uuid4()}.pdf"
    s3 = _get_s3_client()
    s3.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=file_key,
        Body=pdf_bytes,
        ContentType="application/pdf",
    )

    # 5. Deactivate other CVs, create new active one
    CandidateCV.objects.filter(profile=profile, is_active=True).update(is_active=False)
    cv = CandidateCV.objects.create(
        profile=profile,
        name=cv_name,
        template=template_name,
        file=file_key,
        is_active=True,
    )

    # 6. Generate presigned download URL
    download_url = generate_cv_download_url(cv_file_path=file_key)

    return cv, download_url
