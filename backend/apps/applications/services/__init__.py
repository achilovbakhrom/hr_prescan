from apps.applications.services.application_crud import (
    STATUS_TRANSITIONS,
    create_interview_session,
    submit_application,
    update_application_status,
)
from apps.applications.services.bulk_operations import (
    add_hr_note,
    bind_existing_applications,
    bulk_move_by_filter,
    bulk_update_status,
    soft_delete_applications,
)
from apps.applications.services.cv_processing import (
    analyze_cv_with_ai,
    calculate_match_score,
    process_cv_text,
)
from apps.applications.services.s3_utils import (
    _get_s3_client,
    generate_cv_download_url,
    upload_cv_to_s3,
)

# Backward-compatible alias for the old private name
_STATUS_TRANSITIONS = STATUS_TRANSITIONS

__all__ = [
    # application_crud
    "STATUS_TRANSITIONS",
    "_STATUS_TRANSITIONS",
    "create_interview_session",
    "submit_application",
    "update_application_status",
    # bulk_operations
    "add_hr_note",
    "bind_existing_applications",
    "bulk_move_by_filter",
    "bulk_update_status",
    "soft_delete_applications",
    # cv_processing
    "analyze_cv_with_ai",
    "calculate_match_score",
    "process_cv_text",
    # s3_utils
    "_get_s3_client",
    "generate_cv_download_url",
    "upload_cv_to_s3",
]
