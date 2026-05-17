import uuid

from apps.applications.models import Application, ApplicationEvent


def rotate_hiring_manager_token(*, application: Application, actor_name: str = "") -> Application:
    """Rotate the public hiring-manager review token, revoking old share links."""
    application.hiring_manager_token = uuid.uuid4()
    application.save(update_fields=["hiring_manager_token", "updated_at"])
    ApplicationEvent.objects.create(
        application=application,
        event_type=ApplicationEvent.EventType.SHARE_LINK_ROTATED,
        actor_name=actor_name,
        message="Hiring manager review link rotated.",
    )
    return application
