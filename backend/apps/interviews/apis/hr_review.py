from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import HasHRPermission, HRPermissions
from apps.accounts.selectors import get_user_live_company_ids
from apps.common.messages import (
    MSG_INTERVIEW_NOT_FOUND,
    MSG_NO_RECORDING,
    MSG_NOT_IN_COMPANY,
    MSG_RECORDING_ONLY_COMPLETED,
    MSG_TRANSCRIPT_ONLY_COMPLETED,
)
from apps.interviews.models import Interview
from apps.interviews.selectors import (
    get_integrity_flags,
    get_interview_by_id,
)
from apps.interviews.serializers import IntegrityFlagOutputSerializer


class InterviewTranscriptApi(APIView):
    """GET /api/hr/interviews/{id}/transcript/ — timestamped transcript."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_INTERVIEWS

    def get(self, request: Request, interview_id: str) -> Response:
        if not get_user_live_company_ids(user=request.user):
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        interview = get_interview_by_id(
            interview_id=interview_id,
            user=request.user,
        )
        if interview is None:
            return Response(
                {"detail": str(MSG_INTERVIEW_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        if interview.status != Interview.Status.COMPLETED:
            return Response(
                {"detail": str(MSG_TRANSCRIPT_ONLY_COMPLETED)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "interview_id": str(interview.id),
                "transcript": interview.transcript,
            },
            status=status.HTTP_200_OK,
        )


class InterviewRecordingApi(APIView):
    """GET /api/hr/interviews/{id}/recording/ — recording path / presigned URL."""

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_INTERVIEWS

    def get(self, request: Request, interview_id: str) -> Response:
        if not get_user_live_company_ids(user=request.user):
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        interview = get_interview_by_id(
            interview_id=interview_id,
            user=request.user,
        )
        if interview is None:
            return Response(
                {"detail": str(MSG_INTERVIEW_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        if interview.status != Interview.Status.COMPLETED:
            return Response(
                {"detail": str(MSG_RECORDING_ONLY_COMPLETED)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not interview.recording_path:
            return Response(
                {"detail": str(MSG_NO_RECORDING)},
                status=status.HTTP_404_NOT_FOUND,
            )

        # TODO: Generate presigned URL from MinIO/S3 instead of raw path
        return Response(
            {
                "interview_id": str(interview.id),
                "recording_url": interview.recording_path,
            },
            status=status.HTTP_200_OK,
        )


class IntegrityFlagsApi(APIView):
    """GET /api/hr/interviews/{id}/integrity-flags/

    Returns all anti-cheating integrity flags detected during an interview.
    Only available for HR managers and admins scoped to their company.
    """

    permission_classes = [HasHRPermission]
    hr_permission = HRPermissions.MANAGE_INTERVIEWS

    def get(self, request: Request, interview_id: str) -> Response:
        if not get_user_live_company_ids(user=request.user):
            return Response(
                {"detail": str(MSG_NOT_IN_COMPANY)},
                status=status.HTTP_404_NOT_FOUND,
            )

        flags = get_integrity_flags(interview_id=interview_id, user=request.user)
        if flags is None:
            return Response(
                {"detail": str(MSG_INTERVIEW_NOT_FOUND)},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "interview_id": str(interview_id),
                "flags": IntegrityFlagOutputSerializer(flags, many=True).data,
                "total_flags": flags.count(),
            },
            status=status.HTTP_200_OK,
        )
