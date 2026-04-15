"""Backward-compatible re-exports. The actual implementations now live in
``internal_status`` and ``internal_score``.
"""

from apps.interviews.apis.internal_score import InternalInterviewResultsApi
from apps.interviews.apis.internal_status import InternalInterviewContextApi

__all__ = [
    "InternalInterviewContextApi",
    "InternalInterviewResultsApi",
]
