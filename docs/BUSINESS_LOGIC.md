# HR PreScan — Business Logic

## 1. Overview

HR PreScan is a multi-tenant SaaS platform that automates the full candidate screening pipeline using AI-powered conversations via text chat or video. When a vacancy receives hundreds of applicants, manually screening each one is time-consuming and inconsistent.

**The platform provides a two-step AI screening pipeline:**

1. **Prescanning** — an initial AI conversation (always via chat) that quickly filters candidates based on general fit, soft skills, and basic qualifications. Every vacancy has prescanning enabled by default.
2. **Interview** — an optional, more rigorous AI conversation (chat or meet/video) with tougher, domain-specific questions. HR enables this per vacancy by configuring interview questions and criteria.

The AI agent evaluates candidates at each step and decides whether to advance them to the next stage or reject them. HR can also manually move candidates between stages at any time. The platform handles the screening pipeline; HR retains full control over final decisions.

**Platform:** Web application (mobile versions planned for later)
**Languages:** English and Russian (initial release)
**Tech Stack:** Django (backend) + Vue.js (frontend), deployed via Docker Compose with zero-downtime strategy

---

## 2. User Roles

### 2.1 Admin (Platform Admin)
- Manages the entire platform
- User management (create/block/delete companies and users)
- System settings and configuration
- Platform-wide analytics and reporting
- Billing and subscription management
- Monitoring system health

### 2.2 HR Manager
- Belongs to a company (multi-tenant)
- Creates and manages vacancies
- Configures prescanning setup per vacancy (questions, criteria, additional prompt for AI agent)
- Optionally configures interview step per vacancy (questions, criteria, mode, additional prompt for AI agent)
- Reviews candidate scores from both prescanning and interview stages
- Filters and sorts candidates by AI scores
- Manages candidate pipeline per vacancy
- Can manually move candidates between pipeline stages

### 2.3 Candidate
- Can browse public vacancies or access private vacancies via direct link
- No account required to apply or complete prescanning/interview
- Account creation is optional (allows tracking application status and reusing profile across vacancies)
- Uploads CV/resume (optional but recommended)
- Builds and exports a CV through the candidate AI assistant (single chat surface — no separate "AI Generate CV" / "AI Chat" buttons on the CV builder)
- Completes AI prescanning (always via chat) after applying
- If advanced by AI, completes AI interview (chat or meet, depending on vacancy configuration)
- Can start prescanning immediately after applying or return later via the link
- Receives notifications about application status
- Upon registration, previous applications and sessions are automatically linked to the account via email or phone number

---

## 3. Multi-Company Model (per account)

- **The Account is the tenant.** The account is identified by its owner user (`User.account_owner IS NULL ⇒ the user is the owner`). Subscription and billing live on the account owner; plan limits aggregate across every Company in the account.
- **Companies are scoping objects inside the account** (`Company.account_owner`). They group vacancies, applications, and interviews, and double as labels on the public job page.
- **Invitations target the account, not a single company.** When an HR invites a teammate, they pick which companies the invitee gets access to (default: all non-deleted companies at the time of invite). On accept, one `CompanyMembership` is created per selected company and the invitee's `User.account_owner` is set to the inviter's account owner.
- **A user belongs to at most one account.** Accepting an invitation is blocked if the user already owns companies or already belongs to another account — they have to leave the current account first.
- **Default membership per user.** Each user picks one of their memberships as `is_default` — used implicitly for new vacancies and pre-selected in forms.
- **Registration creates the user's own account**: one Company (with the user as `account_owner` and `is_default=True` membership) plus a 14-day trial. Additional companies are added from the **Companies** page.
- **Soft delete** marks `Company.is_deleted=True`: affects every member of that company, transfers each affected user's default to their next non-deleted membership, and historical vacancies keep the company name for display. The acting user cannot delete their last non-deleted company.
- Data isolation: vacancy/application/interview queries scope to the caller's memberships (for invitees) or to all companies on the caller's account (for the owner).
- Company API responses expose the company's country as a human-readable country name. Client create/update requests may still submit the ISO-backed country code selected from the reference list.

---

## 4. Subscription & Billing

### 4.1 Billing Model
- Subscription-based (monthly/yearly, yearly = 2 months free)
- Payment integration (Stripe or similar)
- **Subscription is per-User, not per-Company.** One HR user pays once; plan limits aggregate across every company they own or are a member of.
- 14-day free trial on Pro plan for every new HR user (no credit card required)
- Automatic downgrade to Free when trial expires without payment

### 4.2 Plans

**Free Plan:**
- 1 active vacancy
- 10 AI sessions (prescanning + interviews) per month
- 1 HR user
- Prescanning only (no interview step, no Meet mode)
- 100 MB storage (CVs only, no recordings)
- Community support
- HR PreScan branding on public vacancy pages

**Pro Plan — $49/month ($490/year):**
- 10 active vacancies
- 200 AI sessions per month
- 5 HR users
- Full pipeline: prescanning + interview step with Chat or Meet mode
- 10 GB storage (CVs + interview recordings)
- Email support
- No HR PreScan branding
- Custom company branding on vacancy pages
- Screening analytics dashboard

**Enterprise Plan — custom pricing:**
- Unlimited active vacancies
- Unlimited AI sessions
- Unlimited HR users
- Full pipeline: prescanning + interview step with Chat or Meet mode
- 100 GB storage (expandable)
- Priority support + dedicated account manager
- SSO / SAML integration
- Custom AI prompts and question templates
- API access for ATS integration
- Data residency options (EU, US)
- SLA guarantees (99.9% uptime)

### 4.3 Overage & Limits
- When a limit is reached (vacancies, interviews), the action is blocked with a clear upgrade prompt
- No surprise charges — hard limits, not soft caps
- HR can see current usage vs. limits on the dashboard
- Admin receives email notification at 80% and 100% of monthly interview quota

---

## 5. Vacancy Management

### 5.1 Creating a Vacancy
HR provides the following information:
- **Company** — required. Dropdown lists all companies the user is a member of; pre-selected to their default. The AI vacancy assistant uses the default implicitly if the user has one company, otherwise it asks.
- **Title** — job position name
- **Description** — detailed job description and responsibilities
- **Required Skills** — key skills and qualifications needed
- **Salary Range** — min/max salary (optional, can be hidden from candidates)
- **Location** — remote, onsite, or hybrid (with city/country if applicable)
- **Deadline** — application closing date

### 5.2 Vacancy Visibility & Sharing
- **Public** — listed on the platform's public job board, searchable by anyone
- **Private** — accessible only via a direct shareable link (HR generates and distributes the link)
- HR chooses visibility per vacancy
- **External sharing** — each vacancy has a unique URL that HR can post on external platforms (LinkedIn, job boards, social media, company website). Candidates clicking the link are directed to the vacancy page on PreScan to apply

### 5.3 Vacancy Lifecycle

Vacancies follow a one-directional lifecycle. Once published, a vacancy cannot return to draft.

1. **Draft** — vacancy created but not published. HR configures questions, criteria, and settings.
2. **Published** — live and accepting applications. Can be paused or archived.
3. **Paused** — temporarily not accepting new applications. Can be resumed (back to published) or archived.
4. **Archived** — vacancy is permanently closed. All pending sessions are expired. Cannot be reopened. Can be soft-deleted.

```
Draft → Published ↔ Paused → Archived → (Soft Delete)
                  └──────────→ Archived
```

An HR can manage multiple active vacancies simultaneously.

### 5.3.1 Vacancy Soft Delete

- Only **archived** vacancies can be soft-deleted
- Soft-deleted vacancies are permanently hidden from all views (HR vacancy list, public job board, API)
- Data is retained in the database for compliance/audit purposes but is not accessible through the UI or API
- Related data (applications, sessions, scores) remains intact and linked
- The HR vacancy list is divided into two tabs: **Active** (draft + published + paused) and **Archived**
- The Archived tab shows a delete button per vacancy with a confirmation dialog

### 5.4 Two-Step Screening Pipeline

Each vacancy has a two-step AI screening pipeline. HR configures each step during vacancy creation.

#### 5.4.1 Prescanning (always enabled)

- **Mode:** Always chat — AI converses with the candidate via real-time text messaging in the browser
- **Purpose:** Quick initial screening to filter out clearly unqualified candidates
- **Configuration:**
  - Questions — AI-generated based on vacancy, HR can review/edit/add/remove
  - Evaluation criteria — fixed categories + custom HR-defined criteria (see 7.5)
  - Additional prompt — free-text field where HR writes any instructions for the AI agent (e.g., "Focus on communication skills", "Be lenient with junior candidates")
- No camera or microphone required
- No video recording; the transcript is the primary artifact
- Integrity checks are limited to content-based analysis (response consistency, scripted/AI-generated answer detection)

#### 5.4.2 Interview (optional, enabled per vacancy)

- **Mode:** Chat or Meet — HR chooses per vacancy at creation time
- **Purpose:** Deeper, more rigorous AI evaluation for candidates who passed prescanning
- **To enable:** HR must configure questions and evaluation criteria for the interview step
- **Configuration:**
  - Questions — own set, separate from prescanning questions; tougher and more domain-specific
  - Evaluation criteria — own set, separate from prescanning criteria
  - Additional prompt — free-text field for HR instructions (e.g., "Be strict about technical knowledge", "Test system design thinking")
  - Mode — Chat or Meet
  - Duration — configurable (Meet mode only)
- **Chat mode** — same as prescanning chat, but with interview-specific questions and tougher AI behavior
- **Meet mode** — AI converses with the candidate via a video call on LiveKit. Full integrity monitoring (face detection, gaze tracking, audio anomaly detection). Interview is recorded. Suitable for mid-to-senior roles or positions requiring presentation skills.

#### 5.4.3 Pipeline Rules

- Prescanning mode is always chat and cannot be changed
- Interview mode (chat or meet) is set per vacancy and cannot be changed after the vacancy has active applications
- Both steps produce the same scoring output format: per-criteria scores (1-10), overall weighted score, AI summary, transcript
- Meet mode (interview step only) additionally produces a video recording and integrity flags
- Each step has its own independent set of scores — a candidate will have prescanning scores and (if applicable) interview scores
- CV upload is optional (configurable per vacancy). AI uses CV context in both prescanning and interview if available
- The AI agent decides whether to advance or reject candidates after each step. HR can override at any time.

---

## 6. Candidate Application Flow

Candidates can apply via two surfaces: the **web app** (public job board) and the **Telegram candidate bot** (`@<TELEGRAM_CANDIDATE_BOT_USERNAME>`). Both surfaces produce the same `Application` row and feed the same screening pipeline.

### 6.1 Web flow

1. Candidate finds a vacancy (public job board or direct link)
2. Candidate fills in personal details (name, email, phone). No account required.
3. Candidate uploads CV/resume (optional but recommended; PDF, DOCX supported)
4. System creates the application and simultaneously creates a prescanning session with a unique link
5. Candidate sees a post-apply screen with two options:
   - **"Start Prescanning Now"** — opens the prescanning chat immediately
   - **"I'll do it later"** — saves the prescanning link. The link is also sent via email confirmation.
   - If the vacancy has a Telegram deep-link code, the screen also shows **"Open in Telegram"** so the candidate can continue from the candidate bot on mobile.
6. The prescanning link remains valid until: (a) the vacancy is archived, or (b) the prescanning is completed
7. Candidate receives a confirmation email with: application acknowledgment, prescanning link, vacancy details, and instructions
8. After prescanning completes, AI evaluates and decides:
   - **Advance** — if interview step is enabled, a new interview session is created with a unique link (sent to the candidate via email). If interview step is disabled, the candidate is moved directly to shortlisted.
   - **Reject** — candidate is moved to rejected status
9. If advanced to interview, candidate receives an interview link and completes the interview (chat or meet, depending on vacancy configuration)
10. After interview completes, AI evaluates and decides to shortlist or reject the candidate

#### Candidate-facing Telegram shortcuts

- The public landing page exposes visible Telegram CTAs for both surfaces:
  - a candidate-bot CTA for job seekers
  - an HR-bot CTA for recruiters evaluating the Telegram workflow
- The public HR-bot CTA is discovery-only. Actual HR account linking still happens from the authenticated web app in **Settings -> Telegram**, which generates a one-time deep link for the recruiter's own account.
- Candidate-facing web screens also expose Telegram shortcuts in key places:
  - post-apply / prescanning-ready screen
  - candidate "My Applications" area
  - candidate application detail screen
- When the app knows the vacancy's `telegram_code`, the shortcut uses the vacancy-specific deep link `https://t.me/<bot>?start=vac_<telegram_code>` so the candidate lands in the same vacancy flow inside Telegram.

### 6.2 Telegram bot flow (PR1 — deep-link apply)

The candidate bot lets a candidate go from "I got a link from a friend" to "applied" without ever opening a browser.

1. Someone (HR, friend, job board) shares a deep link `https://t.me/<bot>?start=vac_<vacancy_id>`
2. Candidate opens the link → Telegram launches the bot → bot receives `/start vac_<vacancy_id>`
3. Bot **auto-creates a candidate `User`** if this Telegram identity hasn't been seen before:
   - Email is set to a placeholder `tg_<telegram_id>@telegram.local` (`email_verified=False`) — a real address can be collected later for vacancies that require it
   - First/last name and Telegram username come from the Telegram profile
   - `onboarding_completed=False` so the web app still walks them through onboarding if they ever sign in there
4. Bot fetches the vacancy (must be **published + public** — private/draft/paused vacancies show "no longer available") and renders a vacancy card with `[Apply]` and `[Back]` inline buttons
5. Candidate taps `[Apply]`:
   - If the vacancy has `cv_required=True` and the bot has no CV on file for this user, the bot asks the candidate to send a PDF/DOCX. The pending apply is stored on the bot session, so as soon as the document arrives the apply resumes automatically.
   - Otherwise the bot calls the same `submit_application` service the web flow uses (`apps/applications/services/application_crud.py`). The resulting `Application` is bound to the candidate `User`, so HR sees it identically to web applications.
6. Bot confirms with "✅ Application submitted!" and tells the candidate they'll be DM'd when there's news.
7. **Prescanning interview itself ships in PR2** (in-Telegram chat, text + voice). Until then, candidates who applied via Telegram can complete their prescanning either via the web link (bound to the same `User`) or wait for PR2 to deliver in-bot interviews.

#### Notes & constraints

- One Telegram identity = one `User`. The same person applying via Telegram and via web (with the same email) is reconciled by `bind_existing_applications` once their email is filled in.
- Bot UI is **button-driven** wherever possible (Telegram inline keyboards) — free-text replies are accepted as a fallback and routed to the candidate AI agent (PR2).
- Bot auto-detects language from `message.from.language_code` (en / ru / uz). Strings live in `apps/integrations/telegram_bot/i18n.py`.

---

## 7. AI Screening Process

The platform uses a two-step AI screening pipeline. Each step is an independent AI conversation with its own questions, criteria, scoring, and agent behavior.

### 7.1 CV Analysis (before prescanning)
- When a candidate uploads their CV, AI analyzes it before prescanning begins
- AI extracts: skills, experience, education, languages, job history
- AI compares CV content against vacancy requirements
- AI generates a CV match score
- AI uses CV analysis to tailor prescanning and interview questions (ask about gaps, verify claimed skills, dig into relevant experience)
- If no CV was uploaded, AI skips CV-specific questions and focuses on vacancy requirements

### 7.2 Step 1: Prescanning

Prescanning is the initial AI screening step. It is always enabled and always conducted via chat.

**Setup:**
- Conducted in a browser-based text chat interface
- AI agent sends messages; candidate types responses
- No camera or microphone required
- A typing indicator shows when AI is composing a response
- Messages are persisted server-side — candidate can close the browser and resume later by reopening the prescanning link
- Idle timeout is configurable (default: 24 hours of no activity)
- No time limit — the conversation continues until all questions are covered
- AI decides when enough information has been gathered and wraps up naturally
- A progress indicator shows approximate completion
- Supported languages: English, Russian (candidate or HR selects)

**Question Generation:**
- AI automatically generates prescanning questions based on:
  - Vacancy description and required skills
  - Candidate's CV, if uploaded (tailored questions)
  - Prescanning evaluation criteria set by HR
- HR can review, edit, add, or remove AI-suggested questions before publishing the vacancy
- Questions cover both fixed categories and custom criteria (see 7.5)
- **AI autonomy:** Beyond the HR-specified questions, the AI agent may ask additional questions or follow-ups based on the candidate's answers and CV data. HR-specified questions are the baseline, not the ceiling.
- **Additional prompt:** HR can provide a free-text prompt with extra instructions for the AI agent (e.g., "Focus on communication skills", "Be lenient with junior candidates"). The agent reads and follows this prompt during the conversation.

**Prescanning Flow:**
1. Candidate opens the prescanning link
2. AI greeting message appears immediately
3. AI asks questions one by one; candidate types responses
4. AI can ask follow-up questions or probe deeper based on answers
5. Prescanning concludes when AI determines it has gathered enough information
6. AI thanks the candidate and ends the session
7. Candidate sees a "Thank you" screen with a suggestion to create an account (if unauthenticated)
8. AI evaluates the candidate and produces prescanning scores
9. AI decides: advance to interview (if enabled) or shortlist (if interview disabled) — or reject

### 7.3 Step 2: Interview (optional)

Interview is the second, more rigorous AI screening step. HR enables it per vacancy by configuring interview questions and criteria. The interview AI agent is tougher and more domain-specific than prescanning.

**Setup — Chat mode:**
- Same technical setup as prescanning chat (browser-based text messaging)
- Uses interview-specific questions and criteria (separate from prescanning)
- AI agent behavior is tougher and more probing

**Setup — Meet mode:**
- Conducted in a video room (similar to Google Meet) via LiveKit
- AI agent appears as the interviewer in the room
- Camera and microphone permissions are required
- Candidate sees a device-check preview before joining the room
- Interview duration is configurable by HR per vacancy
- When the time limit is reached, AI wraps up the conversation
- Full integrity monitoring (face detection, gaze tracking, audio anomaly detection)
- Interview is recorded

**Common to both interview modes:**
- A progress indicator shows approximate completion
- Supported languages: English, Russian (candidate or HR selects)

**Question Generation:**
- AI generates interview questions based on:
  - Vacancy description and required skills
  - Candidate's CV, if uploaded
  - Interview evaluation criteria set by HR
  - Prescanning results (AI can reference what was discussed in prescanning to go deeper)
- HR can review, edit, add, or remove AI-suggested questions
- Interview questions are separate from prescanning questions and are typically tougher, more technical, or more domain-specific
- **AI autonomy:** The AI agent may ask additional questions, present practical cases, or challenge the candidate's claims. The agent is expected to be more demanding than during prescanning.
- **Additional prompt:** HR can provide a free-text prompt with extra instructions for the interview AI agent (e.g., "Be strict about technical knowledge", "Test system design thinking", "Present a real-world scenario"). This prompt is separate from the prescanning prompt.

**Interview Flow — Chat mode:**
1. Candidate receives an interview link after being advanced from prescanning
2. Candidate opens the interview link
3. AI greeting message appears
4. AI asks interview questions one by one; candidate types responses
5. AI can ask follow-up questions, present cases, or probe deeper
6. Interview concludes when AI determines it has gathered enough information
7. AI thanks the candidate and ends the session
8. Candidate sees a "Thank you" screen

**Interview Flow — Meet mode:**
1. Candidate receives an interview link after being advanced from prescanning
2. Candidate opens the link and sees a device-check preview (camera, microphone)
3. Candidate clicks "Join Interview"
4. AI agent greets the candidate and explains the process
5. AI asks interview questions one by one, listens to responses
6. AI can ask follow-up questions, present cases, or probe deeper
7. Interview concludes when all questions are covered or time limit is reached
8. AI thanks the candidate and ends the session
9. Candidate sees a "Thank you" screen

**After interview completion:**
- AI evaluates the candidate and produces interview scores (separate from prescanning scores)
- AI decides: shortlist or reject

### 7.3.1 HR Silent Observer Mode (Meet mode only)
- HR can join any active AI interview (meet mode) as a silent observer
- Candidate is NOT notified that HR is watching
- HR can see and hear the interview in real-time but cannot speak or interact
- HR sees the candidate's video and hears both the AI and candidate audio
- This allows HR to get a live impression of promising candidates without disrupting the AI screening process

### 7.5 AI Evaluation & Scoring

Each step (prescanning and interview) produces its own independent set of scores.

**Fixed categories (always scored per step, 1-10 scale):**
- Soft skills (communication, teamwork, adaptability)
- Language proficiency
- Communication clarity
- Motivation and enthusiasm
- Cultural fit

**Custom criteria (defined by HR per step, 1-10 scale):**
- HR adds step-specific criteria (e.g., prescanning: "general React knowledge"; interview: "advanced React architecture")
- AI scores these based on conversation answers and CV data

**Output per candidate per step (both modes):**
- Score for each category (1-10)
- Overall weighted score
- Brief AI summary/notes per category explaining the score
- CV match score (from CV analysis, if CV was uploaded) — shared across steps
- Conversation transcript
- AI decision: advance / shortlist / reject

**Additional output for Meet mode (interview step only):**
- Interview recording (video)
- Integrity flags (see Section 15)

---

## 8. Session Availability

- The AI agent is always available. There is no scheduling step.
- When a candidate applies, a prescanning session is created immediately with a unique link
- The candidate can start prescanning right away or return to it later via the link (sent by email)
- When prescanning completes and AI advances the candidate, an interview session is created automatically with a unique link (sent via email)
- **Session links live as long as the vacancy is published or paused.** There is no time-based expiry — links remain valid until the vacancy is archived or the session is completed.
- If a vacancy is archived while session links are still active:
  - If the candidate has not started: the link becomes invalid, candidate sees "This vacancy is no longer accepting applications." Application status is set to "Expired."
  - If the candidate is mid-session (in progress): the session is allowed to complete. Results are still evaluated and saved.

---

## 9. HR Dashboard & Candidate Review

### 9.1 Dashboard Overview
- List of active vacancies with candidate counts
- Recent screening results (prescanning + interview)
- Key metrics (total applicants, prescreenings completed, interviews completed, average scores)

### 9.2 Candidate Pipeline per Vacancy

Candidates are managed within the vacancy detail page via two views:

**Kanban Board View:**
- Columns: Applied, Prescanned, Interviewed (if interview enabled), Shortlisted, Hired, Rejected, Archived
- Drag-and-drop to move candidates between columns (with confirmation)
- Each card shows: name, email, date, overall score ring, individual score badges (CV %, Prescan /10, Interview /10)
- **Overall score** is a weighted combination: CV 20% + Prescanning 30% + Interview 50% (adapts when scores are missing)
- **Column three-dot menu** with batch actions per column (see 9.5)

**Table View:**
- Columns: Candidate (name + email), Status, Overall score, CV match, Prescan score, Interview score (if enabled), Applied date, Actions
- Checkbox selection for bulk operations (shortlist, hire, reject, archive, reset)
- Per-row three-dot menu with context-aware status changes
- Filtering by status, sorting by date/score
- Search by name or email

### 9.3 Candidate Detail View
- Personal information
- CV viewer (inline PDF/DOCX preview)
- CV match score with breakdown
- **Prescanning results:** scores with AI notes per category, transcript
- **Interview results** (if applicable): scores with AI notes per category, transcript, recording playback (Meet mode only)
- HR can add their own notes
- HR can manually move the candidate to any pipeline status via status dropdown

### 9.4 HR Actions (Individual)

Per-candidate actions available from the detail page or table row menu:
- **Move forward** — advance to the next pipeline stage (Prescanned, Interviewed, Shortlisted, Hired)
- **Shortlist / Hire** — available from any active stage
- **Reject** — available from any active stage
- **Archive** — available from Rejected, Expired, Shortlisted, or Hired
- **Reset to Applied** — restart the pipeline for this candidate
- **Restore** — move archived candidates back to Applied
- **Send email** — contact the candidate via email directly from the platform
- **Messages** — open a messaging thread with the candidate within the platform
- **Reset prescanning/interview** — if a session was abandoned, HR can generate a new link

### 9.5 Batch Operations (Kanban Column Menus)

Each kanban column has a three-dot menu with context-aware batch actions. Actions apply to all candidates in that column.

**Applied column:**
- Reject all / Reject by CV match score < threshold / Reject with no CV / Reject idle > X days
- Shortlist all / Hire all / Archive all

**Prescanned column:**
- Move all to Interviewed (if interview enabled) / Shortlist all / Hire all
- Reject all / Reject by prescanning score < threshold
- Shortlist by prescanning score > threshold / Archive all

**Interviewed column:**
- Shortlist all / Hire all
- Reject all / Reject by interview score < threshold
- Shortlist by interview score > threshold / Archive all

**Shortlisted column:**
- Hire all / Reject all / Archive all

**Hired column:**
- Archive all

**Rejected column:**
- Archive all / Reset all to Applied

**Archived column:**
- Restore all to Applied / Clear all (soft delete — permanently hidden)

**Threshold actions** prompt HR to enter a score value via a dialog before executing.
**Days-based actions** prompt HR to enter a number of days.
All batch actions require confirmation before executing.

### 9.6 Soft Delete

- Candidates in the Archived status can be "cleared" (soft deleted)
- Soft-deleted candidates are permanently hidden from all views — they do not appear in kanban, table, or counts
- Data is retained in the database for compliance/audit purposes but is not accessible through the UI
- This is the mechanism for cleaning up the candidate pipeline after a vacancy is completed

---

## 10. Notifications

### 10.1 Email Notifications
- Candidate: application confirmation with prescanning link, interview link (when advanced), status updates, vacancy closed notification
- HR: new application received, prescanning completed (with score summary), interview completed (with score summary), daily/weekly digest of activity
- Admin: system alerts, new company registrations

### 10.2 In-App Notifications
- Real-time notification center in the web app
- Bell icon with unread count
- Notification types mirror email notifications
- Click-to-navigate to relevant page

---

## 11. Public Job Board

- Landing page showing all public vacancies across companies
- Search and filter by: title, location, salary range, company, skills
- Each vacancy has a detail page with apply button
- SEO-friendly URLs for vacancies
- Company profile pages (name, logo, description, active vacancies)

---

## 12. Candidate Pipeline Statuses (per vacancy)

1. **Applied** — application submitted, prescanning link generated, waiting for candidate to start prescanning. "In progress" state for the prescanning session is tracked on the session object itself, not on the application status.
2. **Prescanned** — prescanning completed, scores generated. If interview step is enabled, an interview link has been generated. If interview step is disabled, AI has recommended this candidate for shortlisting.
3. **Interviewed** — interview completed, scores generated. Only applicable when interview step is enabled for the vacancy.
4. **Shortlisted** — candidate marked as potential hire (by AI decision or HR manual action).
5. **Hired** — candidate has been hired. Terminal success state.
6. **Rejected** — candidate rejected (by AI decision or HR manual action). Can happen at any stage.
7. **Expired** — vacancy was archived before the candidate completed prescanning or interview.
8. **Archived** — candidate moved to archive for cleanup. Can come from Rejected, Expired, Shortlisted, or Hired. Can be soft-deleted (permanently hidden).

**Standard AI-driven pipeline:**
```
Applied → Prescanned → Interviewed* → Shortlisted → Hired
                                                (* if interview enabled)
```

**Full status transitions (including HR manual moves):**
```
Applied → Prescanned, Shortlisted, Hired, Rejected, Archived, Expired

Prescanned → Interviewed (when interview enabled), Shortlisted, Hired,
             Rejected, Archived, Applied (reset)

Interviewed → Shortlisted, Hired, Rejected, Archived, Prescanned (revert)

Shortlisted → Hired, Rejected, Archived, Applied (reset)

Hired → Archived

Rejected → Applied (give another chance), Archived

Expired → Applied (reactivate), Archived

Archived → Applied (restore)
```

**Soft delete:** Archived candidates can be permanently hidden via "Clear archive." Data is retained in the database but not shown in the UI.

---

## 13. Security & Data

- Candidate data is private and isolated per company
- CV files stored securely (encrypted at rest)
- Interview recordings stored securely with access controls (Meet mode only)
- GDPR considerations: candidates can request data deletion
- Authentication: email/password + social login (Google)
- Role-based access control (Admin, HR, Candidate)

### 13.1 Anonymous Access & Account Binding
- Candidates can apply to vacancies and complete prescanning/interviews without creating an account
- Session links contain a UUID token that serves as an unguessable credential, granting access to that specific session only
- Chat mode sessions use the session token for resumption — candidate can close the browser and reopen the link to continue
- Account creation is suggested after the final screening step completion (on the "Thank you" screen and in the confirmation email)
- When a candidate creates an account, the system automatically binds their previous applications and sessions:
  - **Email binding:** matches existing applications where `candidate_email` equals the registered email (case-insensitive)
  - **Phone binding:** matches existing applications where `candidate_phone` equals the registered phone (normalized format)
  - Both matching methods run independently — any match is bound
  - Applications already linked to another account are not re-bound

---

## 14. Company Onboarding Flow

### 14.1 Company Registration

1. Company representative visits the platform and clicks "Register Company"
2. Fills in company details:
   - Company name
   - Industry
   - Company size (number of employees)
   - Country / region
   - Contact person name and email
3. Sets up admin account (email/password)
4. Email verification sent — must confirm before proceeding

### 14.2 Subscription Selection

1. After email verification, company is redirected to pricing page
2. Chooses a subscription plan (or starts a free trial)
3. Enters payment details (credit card via Stripe or similar)
4. Subscription activated — company dashboard becomes accessible

### 14.3 Managing Companies

1. The initial company from signup lands in **Settings → Companies** with `is_default=True`.
2. HR can add more companies at any time from the Companies page. Each additional company starts as non-default.
3. **Set as default** toggles which company is used implicitly (vacancy creation pre-selects it; AI assistant uses it when asked to "use default").
4. **Delete** is a soft delete with a confirm dialog. Cannot delete the user's last non-deleted company. When a company is deleted, every affected user's default is transferred to their next non-deleted company by creation date. Historical vacancies keep the company name for display.
5. Each company can still have its own logo, description, website, size, country, and custom industry. A logo can be uploaded during creation or at any time from the company detail page (PNG/JPG, up to 2 MB). The logo is shown everywhere a company appears — company list, company switcher, vacancy cards, and the public job board. A neutral building-icon placeholder is used when no logo is set.

### 14.4 Inviting HR Users

1. Account admin goes to the "Team" section.
2. Invites HR managers by email and picks which of their companies the invitee should have access to (default: all non-deleted companies at the time of invite).
3. Invitation is scoped to the inviter's account, not to a single company. Only one pending invitation per email per account is allowed at a time.
4. Invitee receives an email listing the account name and the granted companies, with a sign-up / sign-in link.
5. On accept, a `CompanyMembership` is created for each granted company, `User.account_owner` is set to the inviter's account owner, and the invitee lands in the default company. A user who already owns companies (or belongs to another account) cannot accept — they must leave the current account first.
6. Account admin can manage HR permissions (activate/deactivate) and invitation scope for future invites.

### 14.5 Creating First Vacancy

1. After onboarding, the system guides the HR to create their first vacancy
2. A brief tutorial/wizard walks through vacancy creation steps
3. HR configures prescanning (questions, criteria, additional prompt)
4. HR optionally enables and configures interview step (questions, criteria, mode, additional prompt)
5. Once published, the vacancy is live and ready to receive candidates

---

## 15. AI Interview Integrity & Anti-Cheating

### 15.1 Identity Verification (Meet mode — interview step only)

- Before the interview starts, candidate is asked to show an ID document on camera (optional, configurable by HR)
- System takes a photo of the candidate at the start of the interview
- Photo is stored and available for HR to compare with CV photo (if provided)

### 15.2 Behavior Monitoring During Interview (Meet mode — interview step only)

- **Face presence detection** — AI monitors that a face is visible on camera throughout the interview. If the candidate disappears for an extended period, a warning is issued
- **Multiple faces detection** — if more than one person is detected on camera, AI flags it
- **Eye tracking / gaze detection** — AI monitors if the candidate is frequently looking away from the screen (possible sign of reading from notes). This is logged as a note, not an automatic disqualification
- **Audio anomaly detection** — AI detects if another voice is heard or if the candidate appears to be receiving prompts from someone else

### 15.3 Content-Based Cheating Detection (all chat and meet sessions)

- **Response consistency** — AI cross-references answers with CV claims (if CV was uploaded). Inconsistencies are flagged (e.g., claims 5 years of React experience but can't answer basic questions)
- **Scripted answer detection** — AI analyzes response patterns. If answers sound overly rehearsed or read aloud (unnatural pacing, no pauses), it's noted
- **AI-generated answer detection** — if candidate appears to be using ChatGPT or similar tools, this is flagged
- **Response timing analysis (Chat mode)** — suspiciously fast or slow replies may indicate copy-paste from external tools or AI-generated answers
- **Cross-step consistency** — AI can compare prescanning answers with interview answers to detect inconsistencies

### 15.4 Integrity Report

- After each step (prescanning and interview), an integrity section is included in the evaluation
- Flags are shown to HR with severity levels: info, warning, critical
- HR makes the final decision — flags are informational, not automatic rejections
- Examples of flags:
  - "Candidate looked away from screen frequently (12 times)" (Meet mode interview only)
  - "Second person briefly detected at 04:23" (Meet mode interview only)
  - "CV states 5 years Python experience but struggled with basic questions" (any step)
  - "Multiple responses appeared copy-pasted (avg response time: 2 seconds for 200+ word answers)" (Chat mode)
  - "Candidate's interview answers contradict prescanning responses about team management experience" (cross-step)

---

## 16. Edge Cases & Error Handling

### 16.1 Mid-Session Disconnect (Meet mode — interview step only)
- If the candidate's connection drops, the room stays alive for a reconnection window (default: 5 minutes)
- The AI agent pauses and waits for the candidate to rejoin
- If the candidate reconnects within the window, the session resumes from where it left off
- If the candidate does not reconnect, the session is completed with partial data and a note indicating disconnection

### 16.2 Browser Close Mid-Chat (Chat mode — prescanning or interview)
- Chat history is persisted server-side
- Candidate reopens the session link and sees their full conversation history
- The session continues from where it left off
- If no messages are sent for the idle timeout period (default: 24 hours), the session is auto-completed with partial data and a note indicating abandonment

### 16.3 Vacancy Archived During Active Session
- **Session not started (pending):** link becomes invalid, candidate sees "This vacancy is no longer accepting applications"
- **Session in progress:** allowed to complete normally, results are evaluated and saved

### 16.4 Session Retry Policy
- One prescanning session and one interview session per application by default
- If a session was abandoned (started but not finished), HR can manually reset it to generate a new link for the same application
- Candidates cannot self-retry; this prevents gaming the system
- Completed sessions cannot be reset

### 16.5 AI Service Unavailable
- Before connecting the candidate, the system performs a health check on the AI service (Google Gemini for chat, LiveKit agent for meet)
- If the service is unavailable, the candidate sees: "Our interviewer is temporarily unavailable. Please try again in a few minutes."
- System notifies the admin of the outage
- The session status remains "pending" so the candidate can try again later

### 16.6 Concurrent Sessions
- Each candidate's session gets its own independent context (chat thread or video room)
- Multiple candidates can be in prescanning or interview simultaneously for the same vacancy
- No scheduling conflicts since there is no scheduling
- System may enforce per-vacancy concurrency limits to prevent overload (configurable)

### 16.7 Link Sharing Prevention
- **Meet mode (interview):** LiveKit room token is bound to the candidate. Room has max 2 participants (candidate + AI agent). If someone else tries to join with the same link while the session is active, they see "Session is already in use."
- **Chat mode (prescanning or interview):** session token is unique per application. If a session is already active from another browser, the new session takes over (last-writer-wins) to handle legitimate tab switches

### 16.8 CV Processing Timing
- CV parsing is asynchronous (Celery task). If the candidate starts prescanning before CV processing completes:
  - AI proceeds without CV context
  - AI focuses on vacancy-specific questions only
  - Once CV processing completes, the data is available for the evaluation step and subsequent interview step

### 16.9 Vacancy Archival & Session Cleanup
- When a vacancy is archived, all pending (not started) sessions for that vacancy are expired
- Pending sessions have their status set to "Expired"
- Corresponding applications are also set to "Expired"
- Candidate receives an email: "The vacancy you applied for has been closed."
- In-progress sessions are allowed to complete before cleanup
- Archived vacancies cannot be reopened — HR must create a new vacancy if needed

---

## 17. Future Considerations (Post-MVP)

- Mobile applications (iOS, Android)
- Additional languages beyond EN/RU
- Integration with external ATS (Applicant Tracking Systems)
- Integration with job boards (LinkedIn, Indeed, HH.ru)
- Advanced analytics and reporting for companies
- Voice-only interview mode (audio without video)
- Code editor integration for technical chat interviews/prescreening
- Candidate feedback on AI screening experience
- Automated reference checking
- Skill assessment tests (coding challenges, personality tests)
- White-label option for enterprise clients
- Human interviewer mode — HR conducts the interview step instead of AI agent
