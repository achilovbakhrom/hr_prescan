from rest_framework import serializers, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.cv_services import (
    calculate_profile_completeness,
    generate_cv_pdf,
    get_or_create_candidate_profile,
    improve_cv_section,
    parse_cv_with_ai,
)
from apps.accounts.models import (
    CandidateCV,
    CandidateLanguage,
    CandidateProfile,
    Certification,
    Education,
    WorkExperience,
)
from apps.accounts.permissions import IsCandidate
from apps.common.models import EducationLevel, Language, Skill


# ---------------------------------------------------------------------------
# CandidateProfileApi  (GET, PATCH)  /api/candidate/profile/
# ---------------------------------------------------------------------------


class CandidateProfileApi(APIView):
    """
    GET  /api/candidate/profile/ — return full profile with nested relations.
    PATCH /api/candidate/profile/ — update basic profile fields.
    """

    permission_classes = [IsCandidate]

    # -- output serializers ---------------------------------------------------

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
            return {"code": obj.language.code, "name": obj.language.name}

    class CertificationOutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        name = serializers.CharField()
        issuing_organization = serializers.CharField()
        issue_date = serializers.DateField()
        expiry_date = serializers.DateField()
        credential_url = serializers.CharField()
        image = serializers.CharField()
        order = serializers.IntegerField()

    class OutputSerializer(serializers.Serializer):
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
        desired_employment_type = serializers.CharField()
        is_open_to_work = serializers.BooleanField()
        photo = serializers.CharField()
        skills = serializers.SerializerMethodField()
        cvs = serializers.SerializerMethodField()
        work_experiences = serializers.SerializerMethodField()
        educations = serializers.SerializerMethodField()
        languages = serializers.SerializerMethodField()
        certifications = serializers.SerializerMethodField()
        completeness = serializers.SerializerMethodField()

        def get_skills(self, obj):
            return CandidateProfileApi.SkillOutputSerializer(obj.skills.all(), many=True).data

        def get_work_experiences(self, obj):
            return CandidateProfileApi.WorkExperienceOutputSerializer(
                obj.work_experiences.all(), many=True,
            ).data

        def get_educations(self, obj):
            return CandidateProfileApi.EducationOutputSerializer(
                obj.educations.all(), many=True,
            ).data

        def get_languages(self, obj):
            return CandidateProfileApi.LanguageOutputSerializer(
                obj.languages.all(), many=True,
            ).data

        def get_certifications(self, obj):
            return CandidateProfileApi.CertificationOutputSerializer(
                obj.certifications.all(), many=True,
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

    # -- input serializer -----------------------------------------------------

    class InputSerializer(serializers.Serializer):
        headline = serializers.CharField(max_length=255, required=False)
        summary = serializers.CharField(required=False)
        location = serializers.CharField(max_length=255, required=False)
        date_of_birth = serializers.DateField(required=False, allow_null=True)
        linkedin_url = serializers.URLField(max_length=500, required=False, allow_blank=True)
        github_url = serializers.URLField(max_length=500, required=False, allow_blank=True)
        website_url = serializers.URLField(max_length=500, required=False, allow_blank=True)
        desired_salary_min = serializers.DecimalField(
            max_digits=12, decimal_places=2, required=False, allow_null=True,
        )
        desired_salary_max = serializers.DecimalField(
            max_digits=12, decimal_places=2, required=False, allow_null=True,
        )
        desired_salary_currency = serializers.CharField(max_length=3, required=False)
        desired_employment_type = serializers.ChoiceField(
            choices=CandidateProfile.EmploymentType.choices,
            required=False, allow_blank=True,
        )
        is_open_to_work = serializers.BooleanField(required=False)

    # -- handlers -------------------------------------------------------------

    def get(self, request: Request) -> Response:
        profile = get_or_create_candidate_profile(user=request.user)
        profile = (
            CandidateProfile.objects
            .select_related("user")
            .prefetch_related(
                "skills",
                "work_experiences",
                "educations__education_level",
                "languages__language",
                "certifications",
                "cvs",
            )
            .get(pk=profile.pk)
        )
        return Response(self.OutputSerializer(profile).data, status=status.HTTP_200_OK)

    def patch(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = get_or_create_candidate_profile(user=request.user)

        update_fields = []
        for field, value in serializer.validated_data.items():
            setattr(profile, field, value)
            update_fields.append(field)

        if update_fields:
            profile.save(update_fields=update_fields)

        profile = (
            CandidateProfile.objects
            .select_related("user")
            .prefetch_related(
                "skills",
                "work_experiences",
                "educations__education_level",
                "languages__language",
                "certifications",
                "cvs",
            )
            .get(pk=profile.pk)
        )
        return Response(self.OutputSerializer(profile).data, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# CandidateProfileSkillsApi  (PUT)  /api/candidate/profile/skills/
# ---------------------------------------------------------------------------


class CandidateProfileSkillsApi(APIView):
    """PUT /api/candidate/profile/skills/ — replace all skills."""

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        skills = serializers.ListField(
            child=serializers.SlugField(max_length=100),
        )

    class SkillOutputSerializer(serializers.Serializer):
        slug = serializers.CharField()
        name = serializers.CharField()
        category = serializers.CharField()

    def put(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = get_or_create_candidate_profile(user=request.user)
        skill_slugs = serializer.validated_data["skills"]
        skills = Skill.objects.filter(slug__in=skill_slugs)
        profile.skills.set(skills)

        return Response(
            {"skills": self.SkillOutputSerializer(profile.skills.all(), many=True).data},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# WorkExperience CRUD
# ---------------------------------------------------------------------------


class WorkExperienceListCreateApi(APIView):
    """
    GET  /api/candidate/profile/work-experiences/ — list work experiences.
    POST /api/candidate/profile/work-experiences/ — create work experience.
    """

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        company_name = serializers.CharField(max_length=255)
        position = serializers.CharField(max_length=255)
        employment_type = serializers.ChoiceField(
            choices=CandidateProfile.EmploymentType.choices,
            required=False, allow_blank=True, default="",
        )
        location = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
        start_date = serializers.DateField()
        end_date = serializers.DateField(required=False, allow_null=True, default=None)
        is_current = serializers.BooleanField(required=False, default=False)
        description = serializers.CharField(required=False, allow_blank=True, default="")
        order = serializers.IntegerField(required=False, default=0)

    class OutputSerializer(serializers.Serializer):
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

    def get(self, request: Request) -> Response:
        profile = get_or_create_candidate_profile(user=request.user)
        items = profile.work_experiences.all()
        return Response(self.OutputSerializer(items, many=True).data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = get_or_create_candidate_profile(user=request.user)
        item = WorkExperience.objects.create(profile=profile, **serializer.validated_data)

        return Response(self.OutputSerializer(item).data, status=status.HTTP_201_CREATED)


class WorkExperienceDetailApi(APIView):
    """
    PATCH  /api/candidate/profile/work-experiences/<id>/ — update.
    DELETE /api/candidate/profile/work-experiences/<id>/ — delete.
    """

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        company_name = serializers.CharField(max_length=255, required=False)
        position = serializers.CharField(max_length=255, required=False)
        employment_type = serializers.ChoiceField(
            choices=CandidateProfile.EmploymentType.choices,
            required=False, allow_blank=True,
        )
        location = serializers.CharField(max_length=255, required=False, allow_blank=True)
        start_date = serializers.DateField(required=False)
        end_date = serializers.DateField(required=False, allow_null=True)
        is_current = serializers.BooleanField(required=False)
        description = serializers.CharField(required=False, allow_blank=True)
        order = serializers.IntegerField(required=False)

    class OutputSerializer(serializers.Serializer):
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

    def _get_item(self, request, pk):
        profile = get_or_create_candidate_profile(user=request.user)
        try:
            return profile.work_experiences.get(pk=pk)
        except WorkExperience.DoesNotExist:
            return None

    def patch(self, request: Request, pk) -> Response:
        item = self._get_item(request, pk)
        if item is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        update_fields = []
        for field, value in serializer.validated_data.items():
            setattr(item, field, value)
            update_fields.append(field)

        if update_fields:
            item.save(update_fields=update_fields)

        return Response(self.OutputSerializer(item).data, status=status.HTTP_200_OK)

    def delete(self, request: Request, pk) -> Response:
        item = self._get_item(request, pk)
        if item is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Education CRUD
# ---------------------------------------------------------------------------


class EducationListCreateApi(APIView):
    """
    GET  /api/candidate/profile/educations/ — list educations.
    POST /api/candidate/profile/educations/ — create education.
    """

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        institution = serializers.CharField(max_length=255)
        degree = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
        education_level = serializers.SlugField(max_length=50, required=False, allow_null=True, default=None)
        field_of_study = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
        start_date = serializers.DateField(required=False, allow_null=True, default=None)
        end_date = serializers.DateField(required=False, allow_null=True, default=None)
        description = serializers.CharField(required=False, allow_blank=True, default="")
        order = serializers.IntegerField(required=False, default=0)

    class OutputSerializer(serializers.Serializer):
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

    def get(self, request: Request) -> Response:
        profile = get_or_create_candidate_profile(user=request.user)
        items = profile.educations.select_related("education_level").all()
        return Response(self.OutputSerializer(items, many=True).data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        profile = get_or_create_candidate_profile(user=request.user)

        education_level_slug = data.pop("education_level", None)
        education_level = None
        if education_level_slug:
            try:
                education_level = EducationLevel.objects.get(slug=education_level_slug)
            except EducationLevel.DoesNotExist:
                return Response(
                    {"detail": f"Education level '{education_level_slug}' not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        item = Education.objects.create(profile=profile, education_level=education_level, **data)
        item = Education.objects.select_related("education_level").get(pk=item.pk)

        return Response(self.OutputSerializer(item).data, status=status.HTTP_201_CREATED)


class EducationDetailApi(APIView):
    """
    PATCH  /api/candidate/profile/educations/<id>/ — update.
    DELETE /api/candidate/profile/educations/<id>/ — delete.
    """

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        institution = serializers.CharField(max_length=255, required=False)
        degree = serializers.CharField(max_length=255, required=False, allow_blank=True)
        education_level = serializers.SlugField(max_length=50, required=False, allow_null=True)
        field_of_study = serializers.CharField(max_length=255, required=False, allow_blank=True)
        start_date = serializers.DateField(required=False, allow_null=True)
        end_date = serializers.DateField(required=False, allow_null=True)
        description = serializers.CharField(required=False, allow_blank=True)
        order = serializers.IntegerField(required=False)

    class OutputSerializer(serializers.Serializer):
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

    def _get_item(self, request, pk):
        profile = get_or_create_candidate_profile(user=request.user)
        try:
            return profile.educations.select_related("education_level").get(pk=pk)
        except Education.DoesNotExist:
            return None

    def patch(self, request: Request, pk) -> Response:
        item = self._get_item(request, pk)
        if item is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        update_fields = []

        # Handle education_level FK separately
        if "education_level" in data:
            education_level_slug = data.pop("education_level")
            if education_level_slug is None:
                item.education_level = None
            else:
                try:
                    item.education_level = EducationLevel.objects.get(slug=education_level_slug)
                except EducationLevel.DoesNotExist:
                    return Response(
                        {"detail": f"Education level '{education_level_slug}' not found."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            update_fields.append("education_level")

        for field, value in data.items():
            setattr(item, field, value)
            update_fields.append(field)

        if update_fields:
            item.save(update_fields=update_fields)

        item = Education.objects.select_related("education_level").get(pk=item.pk)
        return Response(self.OutputSerializer(item).data, status=status.HTTP_200_OK)

    def delete(self, request: Request, pk) -> Response:
        item = self._get_item(request, pk)
        if item is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# CandidateLanguage CRUD
# ---------------------------------------------------------------------------


class CandidateLanguageListCreateApi(APIView):
    """
    GET  /api/candidate/profile/languages/ — list languages.
    POST /api/candidate/profile/languages/ — create language entry.
    """

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        language = serializers.CharField(max_length=10)
        proficiency = serializers.ChoiceField(choices=CandidateLanguage.Proficiency.choices)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        language = serializers.SerializerMethodField()
        proficiency = serializers.CharField()

        def get_language(self, obj):
            return {"code": obj.language.code, "name": obj.language.name}

    def get(self, request: Request) -> Response:
        profile = get_or_create_candidate_profile(user=request.user)
        items = profile.languages.select_related("language").all()
        return Response(self.OutputSerializer(items, many=True).data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        profile = get_or_create_candidate_profile(user=request.user)

        language_code = data.pop("language")
        try:
            language = Language.objects.get(code=language_code)
        except Language.DoesNotExist:
            return Response(
                {"detail": f"Language '{language_code}' not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check uniqueness
        if profile.languages.filter(language=language).exists():
            return Response(
                {"detail": "This language has already been added to your profile."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        item = CandidateLanguage.objects.create(
            profile=profile, language=language, **data,
        )
        item = CandidateLanguage.objects.select_related("language").get(pk=item.pk)

        return Response(self.OutputSerializer(item).data, status=status.HTTP_201_CREATED)


class CandidateLanguageDetailApi(APIView):
    """
    PATCH  /api/candidate/profile/languages/<id>/ — update.
    DELETE /api/candidate/profile/languages/<id>/ — delete.
    """

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        language = serializers.CharField(max_length=10, required=False)
        proficiency = serializers.ChoiceField(
            choices=CandidateLanguage.Proficiency.choices, required=False,
        )

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        language = serializers.SerializerMethodField()
        proficiency = serializers.CharField()

        def get_language(self, obj):
            return {"code": obj.language.code, "name": obj.language.name}

    def _get_item(self, request, pk):
        profile = get_or_create_candidate_profile(user=request.user)
        try:
            return profile.languages.select_related("language").get(pk=pk)
        except CandidateLanguage.DoesNotExist:
            return None

    def patch(self, request: Request, pk) -> Response:
        item = self._get_item(request, pk)
        if item is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        update_fields = []

        # Handle language FK separately
        if "language" in data:
            language_code = data.pop("language")
            try:
                item.language = Language.objects.get(code=language_code)
            except Language.DoesNotExist:
                return Response(
                    {"detail": f"Language '{language_code}' not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            update_fields.append("language")

        for field, value in data.items():
            setattr(item, field, value)
            update_fields.append(field)

        if update_fields:
            item.save(update_fields=update_fields)

        item = CandidateLanguage.objects.select_related("language").get(pk=item.pk)
        return Response(self.OutputSerializer(item).data, status=status.HTTP_200_OK)

    def delete(self, request: Request, pk) -> Response:
        item = self._get_item(request, pk)
        if item is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# Certification CRUD
# ---------------------------------------------------------------------------


class CertificationListCreateApi(APIView):
    """
    GET  /api/candidate/profile/certifications/ — list certifications.
    POST /api/candidate/profile/certifications/ — create certification.
    """

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255)
        issuing_organization = serializers.CharField(
            max_length=255, required=False, allow_blank=True, default="",
        )
        issue_date = serializers.DateField(required=False, allow_null=True, default=None)
        expiry_date = serializers.DateField(required=False, allow_null=True, default=None)
        credential_url = serializers.URLField(
            max_length=500, required=False, allow_blank=True, default="",
        )
        order = serializers.IntegerField(required=False, default=0)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        name = serializers.CharField()
        issuing_organization = serializers.CharField()
        issue_date = serializers.DateField()
        expiry_date = serializers.DateField()
        credential_url = serializers.CharField()
        image = serializers.CharField()
        order = serializers.IntegerField()

    def get(self, request: Request) -> Response:
        profile = get_or_create_candidate_profile(user=request.user)
        items = profile.certifications.all()
        return Response(self.OutputSerializer(items, many=True).data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = get_or_create_candidate_profile(user=request.user)
        item = Certification.objects.create(profile=profile, **serializer.validated_data)

        return Response(self.OutputSerializer(item).data, status=status.HTTP_201_CREATED)


class CertificationDetailApi(APIView):
    """
    PATCH  /api/candidate/profile/certifications/<id>/ — update.
    DELETE /api/candidate/profile/certifications/<id>/ — delete.
    """

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255, required=False)
        issuing_organization = serializers.CharField(
            max_length=255, required=False, allow_blank=True,
        )
        issue_date = serializers.DateField(required=False, allow_null=True)
        expiry_date = serializers.DateField(required=False, allow_null=True)
        credential_url = serializers.URLField(
            max_length=500, required=False, allow_blank=True,
        )
        order = serializers.IntegerField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        name = serializers.CharField()
        issuing_organization = serializers.CharField()
        issue_date = serializers.DateField()
        expiry_date = serializers.DateField()
        credential_url = serializers.CharField()
        image = serializers.CharField()
        order = serializers.IntegerField()

    def _get_item(self, request, pk):
        profile = get_or_create_candidate_profile(user=request.user)
        try:
            return profile.certifications.get(pk=pk)
        except Certification.DoesNotExist:
            return None

    def patch(self, request: Request, pk) -> Response:
        item = self._get_item(request, pk)
        if item is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        update_fields = []
        for field, value in serializer.validated_data.items():
            setattr(item, field, value)
            update_fields.append(field)

        if update_fields:
            item.save(update_fields=update_fields)

        return Response(self.OutputSerializer(item).data, status=status.HTTP_200_OK)

    def delete(self, request: Request, pk) -> Response:
        item = self._get_item(request, pk)
        if item is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------------------------------------------------------------------------
# ProfileCompletenessApi  (GET)  /api/candidate/profile/completeness/
# ---------------------------------------------------------------------------


class ProfileCompletenessApi(APIView):
    """GET /api/candidate/profile/completeness/ — return profile completeness score."""

    permission_classes = [IsCandidate]

    def get(self, request: Request) -> Response:
        profile = get_or_create_candidate_profile(user=request.user)
        result = calculate_profile_completeness(profile=profile)
        return Response(result, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# CandidateCV CRUD
# ---------------------------------------------------------------------------


class CandidateCVListCreateApi(APIView):
    """
    GET  /api/candidate/profile/cvs/ — list CVs.
    POST /api/candidate/profile/cvs/ — create CV entry.
    """

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255, required=False, default="My CV")
        template = serializers.CharField(max_length=50, required=False, default="classic")

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        name = serializers.CharField()
        template = serializers.CharField()
        file = serializers.CharField()
        is_active = serializers.BooleanField()
        created_at = serializers.DateTimeField()

    def get(self, request: Request) -> Response:
        profile = get_or_create_candidate_profile(user=request.user)
        items = profile.cvs.all()
        return Response(self.OutputSerializer(items, many=True).data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = get_or_create_candidate_profile(user=request.user)
        item = CandidateCV.objects.create(profile=profile, **serializer.validated_data)

        return Response(self.OutputSerializer(item).data, status=status.HTTP_201_CREATED)


class CandidateCVDetailApi(APIView):
    """
    PATCH  /api/candidate/profile/cvs/<id>/ — update CV metadata.
    DELETE /api/candidate/profile/cvs/<id>/ — delete CV.
    """

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255, required=False)
        template = serializers.CharField(max_length=50, required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.UUIDField()
        name = serializers.CharField()
        template = serializers.CharField()
        file = serializers.CharField()
        is_active = serializers.BooleanField()
        created_at = serializers.DateTimeField()

    def _get_item(self, request, pk):
        profile = get_or_create_candidate_profile(user=request.user)
        try:
            return profile.cvs.get(pk=pk)
        except CandidateCV.DoesNotExist:
            return None

    def patch(self, request: Request, pk) -> Response:
        item = self._get_item(request, pk)
        if item is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        update_fields = []
        for field, value in serializer.validated_data.items():
            setattr(item, field, value)
            update_fields.append(field)

        if update_fields:
            item.save(update_fields=update_fields)

        return Response(self.OutputSerializer(item).data, status=status.HTTP_200_OK)

    def delete(self, request: Request, pk) -> Response:
        item = self._get_item(request, pk)
        if item is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CandidateCVActivateApi(APIView):
    """POST /api/candidate/profile/cvs/<id>/activate/ — activate this CV, deactivate others."""

    permission_classes = [IsCandidate]

    def post(self, request: Request, pk) -> Response:
        profile = get_or_create_candidate_profile(user=request.user)
        try:
            cv = profile.cvs.get(pk=pk)
        except CandidateCV.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        cv.activate()
        return Response({"detail": "CV activated.", "id": str(cv.id)}, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# CV Generate PDF
# ---------------------------------------------------------------------------


class CvGeneratePdfApi(APIView):
    """POST /api/candidate/profile/cv/generate-pdf/ — generate PDF from profile."""

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        template = serializers.ChoiceField(
            choices=["classic", "modern", "minimal"], default="classic",
        )
        name = serializers.CharField(max_length=255, required=False, default="My CV")

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = get_or_create_candidate_profile(user=request.user)
        cv, download_url = generate_cv_pdf(
            profile=profile,
            template_name=serializer.validated_data["template"],
            cv_name=serializer.validated_data["name"],
        )

        return Response(
            {
                "id": str(cv.id),
                "name": cv.name,
                "template": cv.template,
                "file": cv.file,
                "is_active": cv.is_active,
                "download_url": download_url,
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# CV Parse (AI)
# ---------------------------------------------------------------------------


class CvParseApi(APIView):
    """POST /api/candidate/profile/cv/parse/ — upload CV file, AI parses and populates profile."""

    permission_classes = [IsCandidate]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request: Request) -> Response:
        cv_file = request.FILES.get("cv_file")
        if not cv_file:
            return Response({"detail": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate file type
        ext = cv_file.name.rsplit(".", 1)[-1].lower() if "." in cv_file.name else ""
        if ext not in ("pdf", "docx"):
            return Response(
                {"detail": "Only PDF and DOCX files are supported."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file_bytes = cv_file.read()
        profile = parse_cv_with_ai(
            user=request.user,
            file_bytes=file_bytes,
            filename=cv_file.name,
        )

        # Return updated profile using the full output serializer
        profile = (
            CandidateProfile.objects
            .select_related("user")
            .prefetch_related(
                "skills",
                "work_experiences",
                "educations__education_level",
                "languages__language",
                "certifications",
                "cvs",
            )
            .get(pk=profile.pk)
        )
        return Response(
            CandidateProfileApi.OutputSerializer(profile).data,
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------------------------
# CV Improve Section (AI)
# ---------------------------------------------------------------------------


class CvImproveSectionApi(APIView):
    """POST /api/candidate/profile/cv/improve-section/ — AI improves a CV section."""

    permission_classes = [IsCandidate]

    class InputSerializer(serializers.Serializer):
        section = serializers.ChoiceField(choices=["summary", "experience_description"])
        content = serializers.CharField()
        job_title = serializers.CharField(required=False, allow_blank=True)

    def post(self, request: Request) -> Response:
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        improved = improve_cv_section(**serializer.validated_data)
        return Response({"improved": improved}, status=status.HTTP_200_OK)
