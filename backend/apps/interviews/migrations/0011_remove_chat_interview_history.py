from django.db import migrations


def remove_chat_interview_history(apps, schema_editor):
    Interview = apps.get_model("interviews", "Interview")
    interview_sessions = Interview.objects.filter(session_type="interview")
    for interview in interview_sessions.iterator():
        update_fields = []
        if interview.screening_mode == "chat":
            interview.screening_mode = "meet"
            interview.transcript = []
            update_fields.extend(["screening_mode", "transcript"])
        if interview.chat_history:
            interview.chat_history = []
            update_fields.append("chat_history")
        if not interview.livekit_room_name:
            interview.livekit_room_name = f"interview-{interview.id}"
            update_fields.append("livekit_room_name")
        if update_fields:
            interview.save(update_fields=[*update_fields, "updated_at"])


class Migration(migrations.Migration):
    dependencies = [
        ("interviews", "0010_interview_decision_support"),
    ]

    operations = [
        migrations.RunPython(remove_chat_interview_history, migrations.RunPython.noop),
    ]
