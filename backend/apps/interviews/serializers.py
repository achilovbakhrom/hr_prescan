from rest_framework import serializers

from apps.interviews.models import Interview, InterviewIntegrityFlag, InterviewScore


class InterviewScoreOutputSerializer(serializers.ModelSerializer):
    """Serializer for per-criteria interview scores."""

    criteria_name = serializers.CharField(source="criteria.name", read_only=True)

    class Meta:
        model = InterviewScore
        fields = [
            "id",
            "criteria",
            "criteria_name",
            "score",
            "ai_notes",
        ]
        read_only_fields = fields


class IntegrityFlagOutputSerializer(serializers.ModelSerializer):
    """Serializer for interview integrity flags."""

    class Meta:
        model = InterviewIntegrityFlag
        fields = [
            "id",
            "flag_type",
            "severity",
            "description",
            "timestamp_seconds",
            "created_at",
        ]
        read_only_fields = fields


class InterviewOutputSerializer(serializers.ModelSerializer):
    """List serializer for interviews."""

    candidate_name = serializers.SerializerMethodField()
    vacancy_title = serializers.SerializerMethodField()

    class Meta:
        model = Interview
        fields = [
            "id",
            "application",
            "candidate_name",
            "vacancy_title",
            "scheduled_at",
            "duration_minutes",
            "status",
            "overall_score",
            "created_at",
        ]
        read_only_fields = fields

    def get_candidate_name(self, obj: Interview) -> str:
        return obj.application.candidate_name

    def get_vacancy_title(self, obj: Interview) -> str:
        return obj.application.vacancy.title


class InterviewDetailOutputSerializer(serializers.ModelSerializer):
    """Detail serializer for interviews, including scores and flags."""

    candidate_name = serializers.SerializerMethodField()
    candidate_email = serializers.SerializerMethodField()
    vacancy_title = serializers.SerializerMethodField()
    scores = InterviewScoreOutputSerializer(many=True, read_only=True)
    integrity_flags = IntegrityFlagOutputSerializer(many=True, read_only=True)

    class Meta:
        model = Interview
        fields = [
            "id",
            "application",
            "candidate_name",
            "candidate_email",
            "vacancy_title",
            "scheduled_at",
            "duration_minutes",
            "status",
            "livekit_room_name",
            "recording_path",
            "transcript",
            "overall_score",
            "ai_summary",
            "scores",
            "integrity_flags",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_candidate_name(self, obj: Interview) -> str:
        return obj.application.candidate_name

    def get_candidate_email(self, obj: Interview) -> str:
        return obj.application.candidate_email

    def get_vacancy_title(self, obj: Interview) -> str:
        return obj.application.vacancy.title


class CandidateInterviewOutputSerializer(serializers.ModelSerializer):
    """Limited view for candidates — room link, scheduled time, no scores."""

    vacancy_title = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = Interview
        fields = [
            "id",
            "vacancy_title",
            "company_name",
            "scheduled_at",
            "duration_minutes",
            "status",
            "livekit_room_name",
            "candidate_token",
        ]
        read_only_fields = fields

    def get_vacancy_title(self, obj: Interview) -> str:
        return obj.application.vacancy.title

    def get_company_name(self, obj: Interview) -> str:
        return obj.application.vacancy.company.name
