"""Speech event compatibility helpers."""


def speech_text(message) -> str:
    """Extract plain text from LiveKit speech events across SDK versions."""
    if isinstance(message, str):
        return message.strip()

    for attr in ("text", "content"):
        value = getattr(message, attr, None)
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, list):
            parts = []
            for item in value:
                if isinstance(item, str):
                    parts.append(item)
                else:
                    item_text = getattr(item, "text", None)
                    if isinstance(item_text, str):
                        parts.append(item_text)
            if parts:
                return " ".join(part.strip() for part in parts if part.strip())

    return str(message).strip()
