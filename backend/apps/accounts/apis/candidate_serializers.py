"""Shared output serializers for candidate profile endpoints."""

from rest_framework import serializers

from apps.accounts.cv_services import calculate_profile_completeness


class SkillOutputSerializer(serializers.Serializer):
    slug = serializers.CharField()
    name = serializers.CharField()
    category = serializers.CharField()


class WorkExperienceOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    company_name = serializers.CharField()
    position = serializers.CharField()
    employment_type = serializers.CharField()
    location = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    is_current = serializers.BooleanField()
    description = serializers.CharField()
    order = serializers.IntegerField()


class EducationOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    institution = serializers.CharField()
    degree = serializers.CharField()
    education_level = serializers.SerializerMethodField()
    field_of_study = serializers.CharField()
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    description = serializers.CharField()
    order = serializers.IntegerField()

    def get_education_level(self, obj):
        if obj.education_level is None:
            return None
        return {"slug": obj.education_level.slug, "name": obj.education_level.name}


class LanguageOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    language = serializers.SerializerMethodField()
    proficiency = serializers.CharField()

    def get_language(self, obj):
        lang = obj.language
        return {"code": lang.code, "name": lang.name, "name_ru": lang.name_ru, "name_uz": lang.name_uz}


class CertificationOutputSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    issuing_organization = serializers.CharField()
    issue_date = serializers.DateField()
    expiry_date = serializers.DateField()
    credential_url = serializers.CharField()
    image = serializers.CharField()
    order = serializers.IntegerField()


class CandidateProfileOutputSerializer(serializers.Serializer):
    """Full profile output used by multiple endpoints."""

    id = serializers.UUIDField()
    headline = serializers.CharField()
    summary = serializers.CharField()
    location = serializers.CharField()
    date_of_birth = serializers.DateField()
    linkedin_url = serializers.CharField()
    github_url = serializers.CharField()
    website_url = serializers.CharField()
    desired_salary_min = serializers.DecimalField(max_digits=12, decimal_places=2)
    desired_salary_max = serializers.DecimalField(max_digits=12, decimal_places=2)
    desired_salary_currency = serializers.CharField()
    desired_salary_negotiable = serializers.BooleanField()
    desired_employment_type = serializers.CharField()
    is_open_to_work = serializers.BooleanField()
    share_token = serializers.CharField()
    photo = serializers.CharField()
    skills = serializers.SerializerMethodField()
    cvs = serializers.SerializerMethodField()
    work_experiences = serializers.SerializerMethodField()
    educations = serializers.SerializerMethodField()
    languages = serializers.SerializerMethodField()
    certifications = serializers.SerializerMethodField()
    completeness = serializers.SerializerMethodField()

    def get_skills(self, obj):
        return SkillOutputSerializer(obj.skills.all(), many=True).data

    def get_work_experiences(self, obj):
        return WorkExperienceOutputSerializer(
            obj.work_experiences.all(),
            many=True,
        ).data

    def get_educations(self, obj):
        return EducationOutputSerializer(
            obj.educations.all(),
            many=True,
        ).data

    def get_languages(self, obj):
        return LanguageOutputSerializer(
            obj.languages.all(),
            many=True,
        ).data

    def get_certifications(self, obj):
        return CertificationOutputSerializer(
            obj.certifications.all(),
            many=True,
        ).data

    def get_completeness(self, obj):
        return calculate_profile_completeness(profile=obj)

    def get_cvs(self, obj):
        cvs = obj.cvs.all()
        return [
            {
                "id": str(cv.id),
                "name": cv.name,
                "template": cv.template,
                "file": cv.file,
                "is_active": cv.is_active,
                "created_at": cv.created_at.isoformat() if cv.created_at else None,
            }
            for cv in cvs
        ]
