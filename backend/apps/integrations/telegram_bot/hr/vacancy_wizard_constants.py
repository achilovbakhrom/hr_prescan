"""Constants for the HR Telegram vacancy creation wizard."""

STATE = "hr_vacancy_wizard"
WIZARD = "vacancy_wizard"
CB_PREFIX = "hr:vw:"
CB_CANCEL = f"{CB_PREFIX}cancel"
CB_BACK = f"{CB_PREFIX}back"
CB_SKIP = f"{CB_PREFIX}skip"
CB_CONFIRM = f"{CB_PREFIX}confirm"
CB_PUBLISH = f"{CB_PREFIX}publish"
CB_DRAFT = f"{CB_PREFIX}draft"
CB_SET_PREFIX = f"{CB_PREFIX}set:"
STEPS = ("company", "title", "description", "skills", "location", "salary", "experience", "interview", "visibility")
