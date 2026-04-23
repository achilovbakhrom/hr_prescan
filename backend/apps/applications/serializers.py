from rest_framework import serializers

from apps.applications.models import Application


class ApplicationListOutputSerializer(serializers.ModelSerializer):
    """Lighter serializer for application lists."""

    vacancy_id = serializers.UUIDField(source="vacancy.id", read_only=True)
    vacancy_title = serializers.CharField(source="vacancy.title", read_only=True)
    prescanning_score = serializers.SerializerMethodField()
    interview_score = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            "id",
            "vacancy_id",
            "candidate_name",
            "candidate_email",
            "cv_file",
            "status",
            "match_score",
            "prescanning_score",
            "interview_score",
            "vacancy_title",
            "created_at",
        ]
        read_only_fields = fields

    def _get_session_score(self, obj: Application, session_type: str) -> float | None:
        # Use prefetched sessions if available
        sessions = getattr(obj, "_prefetched_objects_cache", {}).get("sessions")
        if sessions is not None:
            for s in sessions:
                if s.session_type == session_type and s.status == "completed" and s.overall_score is not None:
                    return float(s.overall_score)
            return None
        # Fallback to query
        from apps.interviews.models import Interview

        session = Interview.objects.filter(application=obj, session_type=session_type, status="completed").first()
        if session and session.overall_score is not None:
            return float(session.overall_score)
        return None

    def get_prescanning_score(self, obj: Application) -> float | None:
        return self._get_session_score(obj, "prescanning")

    def get_interview_score(self, obj: Application) -> float | None:
        return self._get_session_score(obj, "interview")


class ApplicationDetailOutputSerializer(serializers.ModelSerializer):
    """Full detail with parsed data, match score, and match details."""

    vacancy_title = serializers.CharField(source="vacancy.title", read_only=True)
    company_name = serializers.CharField(
        source="vacancy.company.name",
        read_only=True,
    )
    prescan_token = serializers.SerializerMethodField()
    interview_token = serializers.SerializerMethodField()
    interview_enabled = serializers.BooleanField(
        source="vacancy.interview_enabled",
        read_only=True,
    )
    interview_mode = serializers.CharField(
        source="vacancy.interview_mode",
        read_only=True,
    )

    class Meta:
        model = Application
        fields = [
            "id",
            "vacancy_id",
            "vacancy_title",
            "company_name",
            "candidate_name",
            "candidate_email",
            "candidate_phone",
            "cv_file",
            "cv_original_filename",
            "cv_parsed_text",
            "cv_parsed_data",
            "match_score",
            "match_details",
            "match_notes_translations",
            "cv_summary_translations",
            "prescan_token",
            "interview_token",
            "interview_enabled",
            "interview_mode",
            "status",
            "hr_notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def _get_session_token(self, obj: Application, session_type: str) -> str | None:
        session = (
            obj.sessions.filter(session_type=session_type).exclude(status="cancelled").order_by("-created_at").first()
        )
        if session:
            return str(session.interview_token)
        return None

    def get_prescan_token(self, obj: Application) -> str | None:
        return self._get_session_token(obj, "prescanning")

    def get_interview_token(self, obj: Application) -> str | None:
        return self._get_session_token(obj, "interview")


class CandidateApplicationListOutputSerializer(serializers.ModelSerializer):
    """Application list for candidate view — no HR notes or parsed data."""

    vacancy_title = serializers.CharField(source="vacancy.title", read_only=True)
    telegram_code = serializers.IntegerField(source="vacancy.telegram_code", read_only=True, allow_null=True)
    company_name = serializers.CharField(
        source="vacancy.company.name",
        read_only=True,
    )

    class Meta:
        model = Application
        fields = [
            "id",
            "vacancy_title",
            "telegram_code",
            "company_name",
            "status",
            "created_at",
        ]
        read_only_fields = fields


class CandidateApplicationDetailOutputSerializer(serializers.ModelSerializer):
    """Application detail for candidate view — no HR notes or internal data."""

    vacancy_title = serializers.CharField(source="vacancy.title", read_only=True)
    telegram_code = serializers.IntegerField(source="vacancy.telegram_code", read_only=True, allow_null=True)
    company_name = serializers.CharField(
        source="vacancy.company.name",
        read_only=True,
    )
    prescan_token = serializers.SerializerMethodField()
    interview_token = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            "id",
            "vacancy_id",
            "vacancy_title",
            "telegram_code",
            "company_name",
            "candidate_name",
            "candidate_email",
            "candidate_phone",
            "cv_original_filename",
            "prescan_token",
            "interview_token",
            "status",
            "match_score",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def _get_session_token(self, obj: Application, session_type: str) -> str | None:
        session = (
            obj.sessions.filter(session_type=session_type).exclude(status="cancelled").order_by("-created_at").first()
        )
        if session:
            return str(session.interview_token)
        return None

    def get_prescan_token(self, obj: Application) -> str | None:
        return self._get_session_token(obj, "prescanning")

    def get_interview_token(self, obj: Application) -> str | None:
        return self._get_session_token(obj, "interview")
