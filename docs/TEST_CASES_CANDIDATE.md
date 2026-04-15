# Candidate Flow — Test Cases

Comprehensive test cases covering every candidate-facing flow in the platform.

**Legend:**
- **P0** — Critical path, must always work
- **P1** — Important, common scenario
- **P2** — Edge case / less common

---

## 1. Vacancy Discovery

| # | Priority | Case | Steps | Expected Result |
|---|----------|------|-------|-----------------|
| 1.1 | P0 | Browse public job board | Open `/jobs` | Only PUBLISHED + PUBLIC vacancies shown |
| 1.2 | P1 | Search by keyword | Type in search box | Results filtered by title/description/skills |
| 1.3 | P1 | Filter by location | Set location filter | Only matching vacancies shown |
| 1.4 | P1 | Filter by remote | Toggle remote-only | Only `isRemote=true` vacancies |
| 1.5 | P1 | Filter by employment type | Select full-time/part-time/contract/internship | Filtered correctly |
| 1.6 | P1 | Filter by experience level | Select junior/middle/senior/lead/director | Filtered correctly |
| 1.7 | P2 | Filter by salary range | Set min/max salary | Only vacancies within range |
| 1.8 | P0 | View vacancy detail by ID | Open `/jobs/{id}` | Full vacancy info displayed |
| 1.9 | P0 | View vacancy via share link | Open `/jobs/share/{token}` | Vacancy loads (even if private) |
| 1.10 | P1 | View unpublished vacancy by ID | Open `/jobs/{uuid-of-draft}` | 404 — not found |
| 1.11 | P1 | View private vacancy by ID (no share link) | Open `/jobs/{uuid-of-private}` | 404 — visibility check blocks access |
| 1.12 | P2 | View paused vacancy via share link | Open share link for paused vacancy | Vacancy loads (share link bypasses status/visibility check) |
| 1.13 | P2 | Combine multiple filters | Set location + remote + experience | Intersection of all filters applied |
| 1.14 | P2 | Empty search results | Search for gibberish keyword | Empty state shown, no errors |

---

## 2. Application Submission

| # | Priority | Case | Steps | Expected Result |
|---|----------|------|-------|-----------------|
| 2.1 | P0 | Apply without account | Fill name, email, submit | Application created, prescan token returned |
| 2.2 | P0 | Apply while logged in | Submit while authenticated as candidate | Application linked to user account |
| 2.3 | P0 | Apply with CV (optional vacancy) | Upload PDF/DOCX | CV uploaded to S3, async parsing triggered |
| 2.4 | P0 | Apply without CV (CV required vacancy) | Skip CV on `cv_required=true` vacancy | Error: "CV is required" |
| 2.5 | P1 | Apply without CV (CV optional vacancy) | Skip CV upload | Application created successfully |
| 2.6 | P0 | Duplicate application (same email) | Apply twice to same vacancy with same email | Error: "Already applied" |
| 2.7 | P1 | Apply to paused/archived vacancy | Submit to non-PUBLISHED vacancy | Error: "Vacancy not accepting applications" |
| 2.8 | P1 | Apply from share link page | Click Apply on shared vacancy detail page | Navigates to apply page with vacancy UUID (not share token) |
| 2.9 | P1 | Invalid email format | Enter "notanemail" in email field | Frontend validation error |
| 2.10 | P1 | Empty name field | Leave name blank, try submit | Frontend validation error |
| 2.11 | P2 | CV file too large (>10MB) | Upload oversized file | Error from FileUpload component |
| 2.12 | P2 | Invalid CV format | Upload .jpg/.png instead of .pdf/.docx | Rejected by file accept filter |
| 2.13 | P2 | Apply with phone number | Fill optional phone field | Phone saved on application |
| 2.14 | P2 | Apply without phone number | Leave phone blank | Application created, phone is empty |

---

## 3. Post-Submission Flow

| # | Priority | Case | Steps | Expected Result |
|---|----------|------|-------|-----------------|
| 3.1 | P0 | Start prescanning inline | Click "Start Prescanning" on success page | Chat overlay opens with embedded iframe |
| 3.2 | P1 | Open prescanning full-screen | Click expand/external link button | Navigates to `/interview/{token}` |
| 3.3 | P1 | Copy prescan link | Click "Copy Link" button | URL copied to clipboard, button shows "Copied" |
| 3.4 | P0 | Resume prescanning later | Open prescan URL from email/saved link | Chat loads with existing history if session started |
| 3.5 | P1 | Create account after applying | Click "Create Account" link on success page | Register page opens |
| 3.6 | P1 | Minimize chat overlay | Click minimize button | Overlay minimized, bottom bar appears |
| 3.7 | P1 | Re-open minimized chat | Click bottom bar | Chat overlay re-opens |
| 3.8 | P2 | Dismiss prescanning bar | Click X on minimized bar | Bar dismissed |

---

## 4. Prescreening Chat Interview

### 4.1 Session Lifecycle

| # | Priority | Case | Steps | Expected Result |
|---|----------|------|-------|-----------------|
| 4.1.1 | P0 | Start fresh session | Open chat page, session is PENDING | AI greeting message appears, status transitions to IN_PROGRESS |
| 4.1.2 | P0 | Session completes with ADVANCE | Answer questions well | Session completes, application status → PRESCANNED, scores generated |
| 4.1.3 | P0 | Session completes with REJECT | Answer poorly | Session completes, application status → REJECTED, scores generated |
| 4.1.4 | P1 | Session already completed | Open completed interview link | "Interview Completed" message shown, no further input allowed |
| 4.1.5 | P1 | Session cancelled by HR | Open cancelled interview link | Appropriate error message shown |
| 4.1.6 | P2 | Session expired | Open expired interview link | "Link Expired" message |
| 4.1.7 | P2 | Vacancy closed during active session | Vacancy paused/archived while candidate is chatting | Next message fails gracefully |

### 4.2 Text Messages

| # | Priority | Case | Steps | Expected Result |
|---|----------|------|-------|-----------------|
| 4.2.1 | P0 | Send text message | Type message, click send | AI responds contextually within seconds |
| 4.2.2 | P0 | Multi-turn conversation | Send 5+ messages | AI asks relevant follow-ups, references previous answers |
| 4.2.3 | P1 | Send empty message | Try to send blank | Prevented by UI or rejected |
| 4.2.4 | P1 | View chat history on reload | Reload page mid-session | Previous messages load from saved history |
| 4.2.5 | P2 | Send very long message | Paste large text block | Handled without errors |

### 4.3 Voice Messages

| # | Priority | Case | Steps | Expected Result |
|---|----------|------|-------|-----------------|
| 4.3.1 | P1 | Send voice message | Record and send audio | Audio transcribed, AI responds to transcribed text |
| 4.3.2 | P1 | Play back voice message | Click play on sent voice message | Audio streams from S3 and plays |
| 4.3.3 | P2 | Voice message too large (>10MB) | Send oversized audio | Error: file too large |
| 4.3.4 | P2 | Invalid audio format | Send non-audio file via API | Error: invalid file type |

### 4.4 Language Support

| # | Priority | Case | Steps | Expected Result |
|---|----------|------|-------|-----------------|
| 4.4.1 | P0 | Chat in English | Vacancy has `prescanning_language=en` | AI conducts interview in English |
| 4.4.2 | P1 | Chat in Russian | Vacancy has `prescanning_language=ru` | AI conducts interview in Russian |
| 4.4.3 | P1 | Chat in Uzbek | Vacancy has `prescanning_language=uz` | AI conducts interview in Uzbek |
| 4.4.4 | P2 | Candidate responds in wrong language | Respond in English when interview is in Russian | AI handles gracefully, may prompt in correct language |

### 4.5 CV Context

| # | Priority | Case | Steps | Expected Result |
|---|----------|------|-------|-----------------|
| 4.5.1 | P1 | Chat with parsed CV data | Candidate uploaded CV, parsing completed | AI references CV skills/experience in questions |
| 4.5.2 | P1 | Chat without CV | No CV uploaded | AI asks more discovery questions to assess skills |
| 4.5.3 | P2 | Chat with CV still parsing | CV uploaded but async task not done | AI proceeds without CV context |

---

## 5. Scoring & Evaluation

| # | Priority | Case | Steps | Expected Result |
|---|----------|------|-------|-----------------|
| 5.1 | P0 | Scores generated on advance | Complete prescanning successfully | InterviewScore records created for each criterion (1-10) |
| 5.2 | P0 | Scores generated on reject | Complete prescanning with rejection | InterviewScore records still created |
| 5.3 | P0 | Overall score saved | Session completes | `Interview.overall_score` set (1-10 decimal) |
| 5.4 | P0 | AI summary saved | Session completes | `Interview.ai_summary` populated with 2-3 sentence assessment |
| 5.5 | P1 | No criteria configured | Vacancy has no prescanning criteria | Session completes with score=0, summary="No criteria configured" |
| 5.6 | P0 | Auto-create interview session | Prescanning advances + `interview_enabled=true` | New INTERVIEW session created automatically (status=PENDING) |
| 5.7 | P1 | No interview session created | Prescanning advances + `interview_enabled=false` | No interview session, app stays PRESCANNED |
| 5.8 | P1 | Match score calculated | CV uploaded and processed | `Application.match_score` populated (0-100) |
| 5.9 | P1 | Summary translations stored | Complete in non-English language | `ai_summary_translations` contains language-keyed translation |
| 5.10 | P2 | Malformed AI evaluation response | Gemini returns invalid JSON | Session completes with fallback (score=0, error summary) |

---

## 6. Interview Gateway

| # | Priority | Case | Steps | Expected Result |
|---|----------|------|-------|-----------------|
| 6.1 | P0 | Gateway redirects to chat | Open `/interview/{token}`, screening_mode=CHAT | Redirects to `/interview/{token}/chat` |
| 6.2 | P1 | Gateway redirects to video room | Open `/interview/{token}`, screening_mode=MEET | Redirects to `/interview/{token}/room` |
| 6.3 | P1 | Gateway shows completed message | Open token for completed interview | "Interview Completed" shown |
| 6.4 | P1 | Gateway shows expired message | Open token for expired interview | "Link Expired" shown |
| 6.5 | P1 | Gateway shows closed message | Vacancy is paused/archived | "Vacancy Closed" shown |
| 6.6 | P2 | Invalid token | Open `/interview/random-uuid` | 404 error page |

---

## 7. Registration & Login

### 7.1 Email Registration

| # | Priority | Case | Steps | Expected Result |
|---|----------|------|-------|-----------------|
| 7.1.1 | P0 | Register with email | Fill form (email, password, first/last name), submit | Verification email sent, "Check Your Email" screen shown |
| 7.1.2 | P0 | Verify email | Click verification link in email | Account activated, can login |
| 7.1.3 | P1 | Duplicate email | Register with existing email | Error: "User with this email already exists" |
| 7.1.4 | P1 | Password too short | Enter <8 character password | Validation error |
| 7.1.5 | P2 | Login before verification | Try login without verifying email | Error: email not verified |

### 7.2 Login

| # | Priority | Case | Steps | Expected Result |
|---|----------|------|-------|-----------------|
| 7.2.1 | P0 | Login with correct credentials | Enter email + password | JWT tokens returned, redirect to dashboard |
| 7.2.2 | P1 | Login with wrong password | Enter incorrect password | Error message shown |
| 7.2.3 | P1 | Login with non-existent email | Enter unregistered email | Error message shown |
| 7.2.4 | P1 | Token refresh (automatic) | JWT access token expires during session | Auto-refresh happens, request retried seamlessly |
| 7.2.5 | P1 | Both tokens expired | Access + refresh tokens expired | Redirect to login page |
| 7.2.6 | P0 | Logout | Click logout | Tokens cleared, redirect to login |

### 7.3 Social Auth

| # | Priority | Case | Steps | Expected Result |
|---|----------|------|-------|-----------------|
| 7.3.1 | P0 | Google OAuth — new user | Sign in with Google (first time) | Account created, redirect to role selection page |
| 7.3.2 | P1 | Google OAuth — existing user | Sign in with Google again | Logged in directly to dashboard |
| 7.3.3 | P1 | Telegram OAuth — new user | Sign in with Telegram (first time) | Account created (`tg_*@telegram.local`), role selection page |
| 7.3.4 | P0 | Choose candidate role | Select "Candidate" on role page | `onboarding_completed=true`, redirect to dashboard |
| 7.3.5 | P1 | Choose company/employer role | Select "Company" on role page | Company setup form appears |
| 7.3.6 | P1 | Complete company setup | Fill company name, industry, size, country | Company + admin created, redirect to dashboard |
| 7.3.7 | P2 | Telegram user needs email for company | Telegram user picks company role | Email field required (Telegram doesn't provide email) |

---

## 8. My Applications (Authenticated Candidate)

| # | Priority | Case | Steps | Expected Result |
|---|----------|------|-------|-----------------|
| 8.1 | P0 | View applications list | Open `/my-applications` | All user's applications shown in table |
| 8.2 | P0 | View application detail | Click an application | Full status timeline, match score, CV info shown |
| 8.3 | P0 | Status badges correct | Various application statuses | Correct color badges (applied=blue, prescanned=teal, rejected=red, etc.) |
| 8.4 | P1 | Match score pending | CV still being analyzed | Shows "Pending" or "Being Analyzed" indicator |
| 8.5 | P1 | Match score ready | CV analysis complete | Shows percentage (0-100%) |
| 8.6 | P0 | Anonymous apps linked on registration | Register with same email as previous anonymous applications | Previous applications appear in My Applications list |
| 8.7 | P1 | No applications | New account, never applied | Empty state with "Browse Jobs" link |
| 8.8 | P1 | Download CV from detail | Click download on application detail | CV file downloads |
| 8.9 | P2 | Status timeline progression | Application that went through full pipeline | Timeline shows all stages with correct highlights |

---

## 9. CV Builder

| # | Priority | Case | Steps | Expected Result |
|---|----------|------|-------|-----------------|
| 9.1 | P1 | View CV list | Open `/my-cvs` | List of candidate's CVs shown |
| 9.2 | P1 | Create new CV | Select template (classic/modern/minimal), fill sections | CV created and appears in list |
| 9.3 | P1 | AI generate CV | Use AI assistant to generate CV content | CV sections auto-populated |
| 9.4 | P1 | Parse existing CV | Upload existing PDF | Sections extracted and pre-filled |
| 9.5 | P1 | Download CV as PDF | Click download button | PDF generated and downloaded |
| 9.6 | P1 | Activate a CV | Toggle active on one CV | Selected CV active, all others deactivated |
| 9.7 | P1 | Delete CV | Click delete, confirm | CV removed from list |
| 9.8 | P1 | Public CV view | Open `/cv/{shareToken}` | Public page shows CV without authentication |
| 9.9 | P2 | Toggle Open to Work | Switch visibility toggle | `isOpenToWork` updated |
| 9.10 | P2 | Profile completeness score | Fill/skip profile sections | Completeness score updates dynamically |
| 9.11 | P2 | AI improve section | Use "Improve" on a single section | AI refines the section content |
| 9.12 | P2 | AI chat assistant | Open AI chat for CV help | Interactive assistance works |

---

## 10. Notifications

| # | Priority | Case | Steps | Expected Result |
|---|----------|------|-------|-----------------|
| 10.1 | P1 | View notifications | Open notifications page | List of notifications shown |
| 10.2 | P1 | Filter unread only | Toggle "Unread" filter | Only unread notifications shown |
| 10.3 | P1 | Mark notification as read | Click a notification | Marked as read, navigates to related resource |
| 10.4 | P1 | Mark all as read | Click "Mark all read" | All notifications marked as read |
| 10.5 | P1 | Status change notification | HR changes application status | Notification appears for candidate |
| 10.6 | P1 | Interview scheduled notification | HR schedules human interview | Notification + email received |
| 10.7 | P2 | Notification bell badge | New unread notifications | Bell shows unread count badge |
| 10.8 | P2 | Empty notifications | No notifications exist | Empty state shown |

---

## 11. Multi-Company & Invitations

| # | Priority | Case | Steps | Expected Result |
|---|----------|------|-------|-----------------|
| 11.1 | P0 | Accept invitation as new user | Open invitation link, fill name/password | Account created with HR role + assigned permissions |
| 11.2 | P0 | Accept invitation as existing candidate | Already registered, accept invite | CompanyMembership created, can switch companies |
| 11.3 | P0 | Switch to HR company | Use company switcher in navbar | Role/permissions change, HR sidebar items shown |
| 11.4 | P1 | Switch back to candidate context | Switch away from HR company | Candidate sidebar shown, candidate features accessible |
| 11.5 | P1 | Invite email already in company | HR invites email that's already a member | Error: "Already a member of this company" |
| 11.6 | P1 | Cancel pending invitation | HR clicks cancel on pending invitation | Invitation deleted from list |
| 11.7 | P1 | Accept expired invitation | Open invitation link after 7 days | Error: "Invitation expired" |
| 11.8 | P1 | Accept already-accepted invitation | Open invitation link that was already used | Error: "Invitation already accepted" |
| 11.9 | P1 | Permissions applied correctly | HR invites with limited permissions (e.g., only manage_vacancies) | Invited user can only see permitted sidebar items and access permitted APIs |
| 11.10 | P2 | Company switcher only shows with multiple companies | User belongs to 1 company | Static company badge shown (no dropdown) |
| 11.11 | P2 | Company switcher with multiple companies | User belongs to 2+ companies | Dropdown selector shown |

---

## 12. Security & Edge Cases

| # | Priority | Case | Steps | Expected Result |
|---|----------|------|-------|-----------------|
| 12.1 | P0 | Access HR pages as candidate | Navigate to `/vacancies` (HR page) as candidate | Redirect to forbidden page |
| 12.2 | P0 | Access candidate pages as HR | Navigate to `/my-applications` as HR user | Redirect to forbidden page |
| 12.3 | P0 | Access other user's application | Guess application UUID via API | 403 or 404 (scoped to authenticated user) |
| 12.4 | P1 | XSS in application form | Enter `<script>alert(1)</script>` in name field | Sanitized/escaped, no script execution |
| 12.5 | P1 | XSS in chat message | Send `<img onerror=alert(1)>` as chat message | Sanitized, no execution |
| 12.6 | P2 | SQL injection in job search | Enter `'; DROP TABLE--` in search box | No effect (parameterized queries) |
| 12.7 | P1 | Unauthenticated access to /my-applications | Open `/my-applications` without login | Redirect to login page |
| 12.8 | P2 | Rate limiting on apply | Submit 100 applications rapidly | Rate limited after threshold |
| 12.9 | P2 | Concurrent chat messages | Send message while AI is still responding | Queued or rejected gracefully, no duplicate responses |
| 12.10 | P2 | Browser back during chat | Press back button mid-interview | No data loss, can return and continue |

---

## 13. Mobile Responsiveness

| # | Priority | Case | Steps | Expected Result |
|---|----------|------|-------|-----------------|
| 13.1 | P0 | Job board on mobile (375px) | Open `/jobs` on phone | Layout adapts, filters accessible, cards readable |
| 13.2 | P0 | Application form on mobile | Fill form on phone | All fields accessible, submit button visible |
| 13.3 | P0 | Chat interview on mobile | Complete prescreening on phone | Messages readable, input accessible, send works |
| 13.4 | P1 | Chat overlay on mobile | Start prescanning from success page on phone | Overlay fills screen properly |
| 13.5 | P1 | My Applications on mobile | View list/detail on phone | Table scrollable or card layout, readable |
| 13.6 | P1 | Landing page on mobile | Open `/` on phone | Navigation works, sections readable |
| 13.7 | P2 | Voice recording on mobile | Record voice message on phone | Microphone permission requested, recording works |

---

## Test Execution Notes

- **Test accounts needed:** At least 1 candidate, 1 HR admin, 1 HR with limited permissions
- **Test vacancies needed:** 1 published+public, 1 published+private, 1 draft, 1 paused, 1 with cv_required, 1 with interview_enabled
- **Languages to test:** en (primary), ru and uz (at minimum one prescreening each)
- **Browsers:** Chrome, Safari (mobile), Firefox
- **Devices:** Desktop (1440px+), Tablet (768px), Mobile (375px)
