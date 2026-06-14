import logging
from uuid import UUID

from apps.common.exceptions import ApplicationError
from apps.common.messages import MSG_INTERVIEW_NOT_FOUND
from apps.interviews.models import Interview, InterviewIntegrityFlag

logger = logging.getLogger(__name__)


def add_integrity_flag(
    *,
    interview: Interview,
    flag_type: str,
    severity: str,
    description: str,
    timestamp_seconds: int | None = None,
) -> InterviewIntegrityFlag:
    """Create an integrity flag for an interview."""
    return InterviewIntegrityFlag.objects.create(
        interview=interview,
        flag_type=flag_type,
        severity=severity,
        description=description,
        timestamp_seconds=timestamp_seconds,
    )


def create_integrity_flags(
    *,
    interview_id: UUID,
    flags_data: list[dict],
) -> list[InterviewIntegrityFlag]:
    """Bulk-create IntegrityFlag records for an interview.

    Args:
        interview_id: UUID of the interview to attach flags to.
        flags_data: List of dicts with keys: flag_type, severity, description,
                    and optionally timestamp_seconds.

    Returns:
        List of created InterviewIntegrityFlag instances.
    """
    try:
        interview = Interview.objects.get(id=interview_id)
    except Interview.DoesNotExist:
        raise ApplicationError(str(MSG_INTERVIEW_NOT_FOUND)) from None

    flag_objects = [
        InterviewIntegrityFlag(
            interview=interview,
            flag_type=flag["flag_type"],
            severity=flag["severity"],
            description=flag["description"],
            timestamp_seconds=flag.get("timestamp_seconds"),
        )
        for flag in flags_data
    ]

    created = InterviewIntegrityFlag.objects.bulk_create(flag_objects)
    logger.info("Created %d integrity flags for interview %s.", len(created), interview_id)
    return created
