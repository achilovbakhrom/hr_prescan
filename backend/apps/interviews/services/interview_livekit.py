import os

from livekit.api import AccessToken, VideoGrants

from apps.common.exceptions import ApplicationError
from apps.interviews.models import Interview

LIVEKIT_API_KEY = os.environ.get("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.environ.get("LIVEKIT_API_SECRET", "")


def _create_livekit_token(
    *,
    room_name: str,
    participant_identity: str,
    participant_name: str,
    can_publish: bool = True,
    can_subscribe: bool = True,
) -> str:
    """Create a LiveKit access token with the given grants."""
    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        raise ApplicationError(
            "LiveKit credentials not configured. "
            "Set LIVEKIT_API_KEY and LIVEKIT_API_SECRET."
        )

    token = (
        AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        .with_identity(participant_identity)
        .with_name(participant_name)
        .with_grants(
            VideoGrants(
                room=room_name,
                room_join=True,
                can_publish=can_publish,
                can_subscribe=can_subscribe,
            )
        )
    )
    return token.to_jwt()


def generate_candidate_token(*, interview: Interview) -> str:
    """Generate a LiveKit participant token for the candidate."""
    return _create_livekit_token(
        room_name=interview.livekit_room_name,
        participant_identity=f"candidate-{interview.application.id}",
        participant_name=interview.application.candidate_name,
        can_publish=True,
        can_subscribe=True,
    )


def generate_observer_token(*, interview: Interview) -> str:
    """Generate a LiveKit observer token for HR to watch live (no publishing)."""
    return _create_livekit_token(
        room_name=interview.livekit_room_name,
        participant_identity=f"observer-{interview.id}",
        participant_name="HR Observer",
        can_publish=False,
        can_subscribe=True,
    )
