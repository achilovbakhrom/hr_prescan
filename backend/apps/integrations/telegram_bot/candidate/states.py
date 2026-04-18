"""Session state constants for the candidate bot conversation flow."""

# Registration states — used when user.phone is not yet set
STATE_REG_NAME = "reg_name"
STATE_REG_PHONE = "reg_phone"

# Prescreening flow states
STATE_PS_CODE = "ps_code"  # waiting for 6-digit vacancy code
STATE_PS_CONFIRM_NAME = "ps_confirm_name"  # show stored name, ask confirm/change
STATE_PS_CHANGE_NAME = "ps_change_name"  # waiting for new name text
STATE_PS_CONFIRM_PHONE = "ps_confirm_phone"  # show stored phone, ask confirm/change
STATE_PS_CHANGE_PHONE = "ps_change_phone"  # waiting for new phone text
STATE_PS_CV = "ps_cv"  # waiting for CV upload (or skip)
STATE_PS_INTERVIEW = "ps_interview"  # answering interview questions

# Session data keys
SK_VACANCY_ID = "ps_vacancy_id"
SK_NAME = "ps_name"
SK_PHONE = "ps_phone"
SK_CV_PATH = "ps_cv_path"
SK_CV_FILENAME = "ps_cv_filename"
SK_INTERVIEW_ID = "ps_interview_id"
SK_QUESTION_IDX = "ps_question_idx"
SK_QUESTION_COUNT = "ps_question_count"
SK_REG_NAME = "reg_name_value"
