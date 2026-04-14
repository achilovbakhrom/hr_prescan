"""
Centralized translatable messages for API responses and service errors.

All user-facing strings are defined here using gettext_lazy so they are
translated at render time based on the active language (determined by the
Accept-Language header via Django's LocaleMiddleware).
"""

from django.utils.translation import gettext_lazy as _

# Common
MSG_NOT_FOUND = _("Not found.")
MSG_FORBIDDEN = _("You do not have permission to perform this action.")

# Auth
MSG_USER_EXISTS = _("User with this email already exists.")
MSG_INVALID_CREDENTIALS = _("Invalid email or password.")
MSG_ACCOUNT_DEACTIVATED = _("Account is deactivated.")
MSG_EMAIL_ALREADY_VERIFIED = _("Email is already verified.")
MSG_INVALID_VERIFICATION_TOKEN = _("Invalid or expired verification token.")
MSG_REGISTRATION_SUCCESS = _("Registration successful. Please verify your email.")
MSG_EMAIL_VERIFIED = _("Email verified successfully.")
MSG_LOGOUT_SUCCESS = _("Logout successful.")
MSG_INVALID_TOKEN = _("Invalid or expired token.")
MSG_INVALID_REFRESH_TOKEN = _("Invalid or expired refresh token.")
MSG_INVALID_GOOGLE_TOKEN = _("Invalid Google token.")
MSG_GOOGLE_NO_EMAIL = _("Google account has no email.")

# Company
MSG_NOT_IN_COMPANY = _("You are not associated with a company.")
MSG_COMPANY_REGISTERED = _("Company registered successfully. Please verify your email.")
MSG_INVITATION_SENT = _("Invitation sent successfully.")
MSG_INVITATION_EXISTS = _("An invitation has already been sent to this email.")
MSG_INVITATION_ACCEPTED = _("Invitation accepted. You can now log in.")
MSG_INVITATION_ACCEPTED_COMPANY = _("Invitation accepted. You are now part of the company.")
MSG_INVALID_INVITATION = _("Invalid invitation token.")
MSG_INVITATION_ALREADY_ACCEPTED = _("This invitation has already been accepted.")
MSG_INVITATION_EXPIRED = _("This invitation has expired.")
MSG_INVITATION_WRONG_EMAIL = _("This invitation was sent to a different email.")
MSG_USER_NOT_FOUND = _("User not found.")

# User management
MSG_ONLY_ADMINS_DEACTIVATE = _("Only admins can deactivate users.")
MSG_ONLY_ADMINS_ACTIVATE = _("Only admins can activate users.")
MSG_MANAGE_OWN_COMPANY = _("You can only manage users in your own company.")
MSG_CANNOT_DEACTIVATE_SELF = _("You cannot deactivate yourself.")
MSG_USER_ALREADY_DEACTIVATED = _("User is already deactivated.")
MSG_USER_ALREADY_ACTIVE = _("User is already active.")

# Vacancies
MSG_VACANCY_NOT_FOUND = _("Vacancy not found.")
MSG_VACANCY_NOT_ACCEPTING = _("This vacancy is not accepting applications.")
MSG_CV_REQUIRED = _("A CV is required for this vacancy.")
MSG_ALREADY_APPLIED = _("You have already applied to this vacancy.")
MSG_CANNOT_CHANGE_MODE = _("Cannot change interview mode after applications have been submitted.")
MSG_ONLY_DRAFT_PAUSED_PUBLISH = _("Only draft or paused vacancies can be published.")
MSG_NO_PRESCANNING_QUESTIONS = _("Cannot publish a vacancy without active prescanning questions.")
MSG_NO_INTERVIEW_QUESTIONS = _("Cannot publish a vacancy with interview enabled but no active interview questions.")
MSG_ONLY_PUBLISHED_PAUSE = _("Only published vacancies can be paused.")
MSG_ONLY_PUBLISHED_PAUSED_ARCHIVE = _("Only published or paused vacancies can be archived.")
MSG_ONLY_ARCHIVED_DELETE = _("Only archived vacancies can be deleted.")
MSG_FILE_EXTRACT_FAILED = _("Could not extract text from the uploaded file.")
MSG_AI_COMPANY_INFO_FAILED = _("Failed to generate company info. Please try again.")
MSG_INTERNAL_URL_NOT_ALLOWED = _("Internal or private URLs are not allowed.")
MSG_INVALID_URL = _("Invalid URL.")
MSG_URL_RESOLVE_FAILED = _("Could not resolve the URL hostname.")
MSG_WEBSITE_FETCH_FAILED = _("Could not fetch the website.")
MSG_WEBSITE_EXTRACT_FAILED = _("Could not extract text from the website.")
MSG_AI_QUESTIONS_FAILED = _("Failed to generate questions. Please try again.")
MSG_CRITERIA_NOT_FOUND = _("Criteria not found.")
MSG_QUESTION_NOT_FOUND = _("Question not found.")

# Applications
MSG_APPLICATION_NOT_FOUND = _("Application not found.")
MSG_STATUS_TRANSITION_INVALID = _("Cannot transition from '{current}' to '{target}'.")
MSG_NO_CV_UPLOADED = _("No CV uploaded for this application.")

# Interviews
MSG_INTERVIEW_NOT_FOUND = _("Interview not found.")
MSG_CANNOT_CANCEL_SESSION = _("Cannot cancel session with status '{status}'.")
MSG_CANNOT_START_SESSION = _("Cannot start interview with status '{status}'.")
MSG_NOT_CHAT_MODE = _("This session is not a chat-mode session.")
MSG_SESSION_NOT_IN_PROGRESS = _("This session is not currently in progress.")
MSG_NO_FILE_UPLOADED = _("No file uploaded.")
MSG_FILE_TOO_LARGE = _("File too large. Maximum size is 10MB.")
MSG_UNSUPPORTED_FILE_TYPE = _("Unsupported file type.")
MSG_AUDIO_TRANSCRIPTION_FAILED = _("Audio transcription failed.")
MSG_AUDIO_NOT_FOUND = _("Audio file not found.")
MSG_INVALID_AUDIO_URL = _("Invalid audio URL.")
MSG_NO_AUDIO_FILE = _("This message does not have an associated audio file.")
MSG_MESSAGE_INDEX_OUT_OF_RANGE = _("Message index out of range.")
MSG_EVALUATION_MALFORMED = _(
    "AI evaluation completed but the scoring response was malformed. "
    "HR should review the conversation transcript manually."
)
MSG_NO_SESSION_FOUND = _("No session found for this application.")
MSG_CHAT_ONLY = _("Chat is only available for chat-mode interviews.")
MSG_CHAT_HISTORY_ONLY = _("Chat history is only available for chat-mode interviews.")
MSG_VOICE_ONLY = _("Voice messages are only available for chat-mode interviews.")
MSG_VACANCY_NOT_ACCEPTING_INTERVIEWS = _("This vacancy is no longer accepting interviews.")
MSG_TRANSCRIPT_ONLY_COMPLETED = _("Transcript is only available for completed interviews.")
MSG_RECORDING_ONLY_COMPLETED = _("Recording is only available for completed interviews.")
MSG_NO_RECORDING = _("No recording available for this interview.")
MSG_AUDIO_FILE_REQUIRED = _("audio_file is required.")
MSG_AUDIO_FILE_TOO_LARGE = _("Audio file exceeds maximum size of 10 MB.")
MSG_INVALID_AUDIO_FILE_TYPE = _("Invalid file type. Only audio files are accepted.")
MSG_INTERVIEW_RESULTS_SAVED = _("Interview results saved successfully.")
MSG_INVALID_INTERNAL_KEY = _("Invalid or missing internal API key.")

# Employer Companies
MSG_EMPLOYER_NOT_FOUND = _("Employer company not found.")
MSG_EMPLOYER_HAS_VACANCIES = _("Cannot delete employer with linked vacancies.")
