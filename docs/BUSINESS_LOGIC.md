# HR PreScan — Business Logic

## 1. Overview

HR PreScan is a multi-tenant SaaS platform that automates the candidate pre-screening process using AI-powered interviews via text chat or video. When a vacancy receives hundreds of applicants, manually screening each one is time-consuming and inconsistent.

**The core goal of the platform is to help HR pre-filter candidates.** The AI conducts structured interviews (text chat or video), analyzes CVs, and scores candidates — so HR doesn't have to spend time on every applicant. After reviewing AI results, HR decides what to do with qualified candidates: schedule a full interview, start a direct chat, or take any next step they see fit. The platform handles the screening; HR handles the final decision-making.

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
- Chooses screening mode per vacancy (chat or meet)
- Configures AI interview parameters (duration, questions, criteria)
- Reviews candidate scores and interview results
- Filters and sorts candidates by AI scores
- Manages candidate pipeline per vacancy

### 2.3 Candidate
- Can browse public vacancies or access private vacancies via direct link
- No account required to apply or complete an interview
- Account creation is optional (allows tracking application status and reusing profile across vacancies)
- Uploads CV/resume (optional but recommended)
- Takes AI pre-screening interview (chat or video, depending on vacancy configuration)
- Can start the interview immediately after applying or return later via the interview link
- Receives notifications about application status
- Upon registration, previous applications and interviews are automatically linked to the account via email or phone number

---

## 3. Multi-Tenancy (Company Model)

- Multiple companies can register and use the platform independently
- Each company has its own:
  - HR managers
  - Vacancies
  - Candidate pools
  - Subscription plan
- Data is isolated between companies
- Companies sign up and choose a subscription plan

---

## 4. Subscription & Billing

### 4.1 Billing Model
- Subscription-based (monthly/yearly, yearly = 2 months free)
- Payment integration (Stripe or similar)
- 14-day free trial on Pro plan for new companies (no credit card required)
- Automatic downgrade to Free when trial expires without payment

### 4.2 Plans

**Free Plan:**
- 1 active vacancy
- 10 AI interviews per month
- 1 HR user
- Chat screening mode only
- 100 MB storage (CVs only, no recordings)
- Community support
- HR PreScan branding on public vacancy pages

**Pro Plan — $49/month ($490/year):**
- 10 active vacancies
- 200 AI interviews per month
- 5 HR users
- Chat + Meet screening modes
- 10 GB storage (CVs + interview recordings)
- Email support
- No HR PreScan branding
- Custom company branding on vacancy pages
- Interview analytics dashboard

**Enterprise Plan — custom pricing:**
- Unlimited active vacancies
- Unlimited AI interviews
- Unlimited HR users
- Chat + Meet screening modes
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
1. **Draft** — vacancy created but not published
2. **Active** — published and accepting applications
3. **Paused** — temporarily not accepting new applications
4. **Closed** — vacancy filled or cancelled, no longer accepting applications

An HR can manage multiple active vacancies simultaneously.

### 5.4 Screening Mode

HR chooses one screening mode per vacancy at creation time:

- **Chat (Simple)** — AI interviews the candidate via real-time text messaging in the browser. Lower friction: no camera or microphone permissions needed. Suitable for high-volume roles and initial screening. The AI agent uses the same LLM and question set but communicates via text. No video recording; the transcript is the primary artifact. Integrity checks are limited to content-based analysis (response consistency, scripted/AI-generated answer detection). No face or gaze detection.

- **Meet (Advanced)** — AI interviews the candidate via a video call on LiveKit. Full integrity monitoring (face detection, gaze tracking, audio anomaly detection). Interview is recorded. This is the premium mode suitable for mid-to-senior roles or positions requiring presentation skills.

**Rules:**
- Screening mode is set per vacancy and cannot be changed after the vacancy has active applications (ensures consistent evaluation across all candidates for the same role)
- Both modes produce the same scoring output: per-criteria scores (1-10), overall weighted score, AI summary, transcript
- Meet mode additionally produces a video recording and integrity flags
- CV upload is optional (configurable per vacancy). AI interviews with or without CV context; without CV, AI focuses on vacancy-specific questions only

---

## 6. Candidate Application Flow

1. Candidate finds a vacancy (public job board or direct link)
2. Candidate fills in personal details (name, email, phone). No account required.
3. Candidate uploads CV/resume (optional but recommended; PDF, DOCX supported)
4. System creates the application and simultaneously creates an interview session with a unique interview link
5. Candidate sees a post-apply screen with two options:
   - **"Start Interview Now"** — opens the interview immediately (chat or video, depending on vacancy screening mode)
   - **"I'll do it later"** — saves the interview link. The link is also sent via email confirmation.
6. The interview link remains valid until: (a) the vacancy is closed, or (b) the interview is completed
7. Candidate receives a confirmation email with: application acknowledgment, interview link, vacancy details, and instructions for the interview mode (chat vs. video)

---

## 7. AI Interview Process

### 7.1 Pre-Interview: CV Analysis
- When a candidate uploads their CV, AI analyzes it before the interview
- AI extracts: skills, experience, education, languages, job history
- AI compares CV content against vacancy requirements
- AI generates a CV match score
- AI uses CV analysis to tailor interview questions (ask about gaps, verify claimed skills, dig into relevant experience)
- If no CV was uploaded, AI skips CV-specific questions and focuses on vacancy requirements

### 7.2 Interview Setup

**Chat mode:**
- Interview is conducted in a browser-based text chat interface
- AI agent sends messages; candidate types responses
- No camera or microphone required
- A typing indicator shows when AI is composing a response
- Messages are persisted server-side — candidate can close the browser and resume later by reopening the interview link
- Idle timeout is configurable (default: 24 hours of no activity)

**Meet mode:**
- Interview is conducted in a video room (similar to Google Meet)
- AI agent appears as the interviewer in the room
- Camera and microphone permissions are required
- Candidate sees a device-check preview before joining the room

**Chat mode specifics:**
- No time limit — the conversation continues until all questions are covered
- AI decides when enough information has been gathered and wraps up naturally

**Meet mode specifics:**
- Interview duration is configurable by HR per vacancy
- When the time limit is reached, AI wraps up the conversation

**Common to both modes:**
- A progress indicator shows approximate interview completion
- Supported languages: English, Russian (candidate or HR selects)

### 7.3 Interview Question Generation
- AI automatically generates interview questions based on:
  - Vacancy description and required skills
  - Candidate's CV, if uploaded (tailored questions)
  - Evaluation criteria set by HR
- HR can review, edit, add, or remove AI-suggested questions before publishing the vacancy
- Questions cover both fixed categories and custom criteria (see 7.5)
- **AI autonomy:** Beyond the HR-specified questions, the AI agent may ask additional job-related questions, follow-up questions, or present practical cases if it sees a reason to clarify or dig deeper. The AI uses its judgment based on the candidate's answers, CV data, and the vacancy context. HR-specified questions are the baseline, not the ceiling.

### 7.4 Interview Flow

**Chat mode:**
1. Candidate opens the interview link
2. AI greeting message appears immediately
3. AI asks questions one by one; candidate types responses
4. AI can ask follow-up questions, present cases, or probe deeper based on answers
5. Interview concludes when AI determines it has gathered enough information
6. AI thanks the candidate and ends the session
7. Candidate sees a "Thank you" screen with a suggestion to create an account (if unauthenticated)

**Meet mode:**
1. Candidate opens the interview link and sees a device-check preview (camera, microphone)
2. Candidate clicks "Join Interview"
3. AI agent greets the candidate and explains the process
4. AI asks questions one by one, listens to responses
5. AI can ask follow-up questions, present cases, or probe deeper based on answers
6. Interview concludes when all questions are covered or time limit is reached
7. AI thanks the candidate and ends the session
8. Candidate sees a "Thank you" screen with a suggestion to create an account (if unauthenticated)

### 7.4.1 HR Silent Observer Mode (Meet mode only)
- HR can join any active AI interview as a silent observer
- Candidate is NOT notified that HR is watching
- HR can see and hear the interview in real-time but cannot speak or interact
- HR sees the candidate's video and hears both the AI and candidate audio
- This allows HR to get a live impression of promising candidates without disrupting the AI screening process

### 7.5 AI Evaluation & Scoring
After the interview, AI evaluates the candidate on:

**Fixed categories (always scored, 1-10 scale):**
- Soft skills (communication, teamwork, adaptability)
- Language proficiency
- Communication clarity
- Motivation and enthusiasm
- Cultural fit

**Custom criteria (defined by HR per vacancy, 1-10 scale):**
- HR adds vacancy-specific criteria (e.g., "React experience", "leadership skills", "system design knowledge")
- AI scores these based on interview answers and CV data

**Output per candidate (both modes):**
- Score for each category (1-10)
- Overall weighted score
- Brief AI summary/notes per category explaining the score
- CV match score (from pre-interview analysis, if CV was uploaded)
- Interview transcript

**Additional output for Meet mode:**
- Interview recording (video)
- Integrity flags (see Section 15)

---

## 8. Interview Availability

- The AI agent is always available. There is no scheduling step.
- When a candidate applies, an interview session is created immediately with a unique link
- The candidate can start the interview right away or return to it later via the link (sent by email)
- **Interview links live as long as the vacancy is open.** There is no time-based expiry — the link remains valid until the vacancy is closed or the interview is completed.
- If a vacancy is closed while interview links are still active:
  - If the candidate has not started: the link becomes invalid, candidate sees "This vacancy is no longer accepting applications." Application status is set to "Expired."
  - If the candidate is mid-interview (in progress): the interview is allowed to complete. Results are still evaluated and saved.

---

## 9. HR Dashboard & Candidate Review

### 9.1 Dashboard Overview
- List of active vacancies with candidate counts
- Recent interview results
- Key metrics (total applicants, interviews completed, average scores)

### 9.2 Candidate List per Vacancy
- Table/list of all candidates for a vacancy
- Columns: name, application date, interview status, overall score, individual category scores
- **Filtering:** by score range, by category scores, by interview status
- **Sorting:** by any score category, by date, by overall score
- **Search:** by candidate name or keywords

### 9.3 Candidate Detail View
- Personal information
- CV viewer (inline PDF/DOCX preview)
- CV match score with breakdown
- Interview scores with AI notes per category
- Interview recording playback (Meet mode only)
- Interview transcript
- HR can add their own notes
- HR can mark candidate status: reviewing, shortlisted, rejected

### 9.4 HR Actions After AI Screening

Once HR reviews AI scores and decides a candidate is worth pursuing, they can:
- **Schedule a full interview** — set up a real (human) interview with the candidate, with calendar integration
- **Start a direct chat** — open a messaging thread with the candidate within the platform
- **Send an email** — contact the candidate via email directly from the platform
- **Reject** — mark the candidate as rejected (with optional reason)
- **Reset interview** — if a candidate's interview was abandoned (started but not finished), HR can generate a new interview link for the same application

The platform does not dictate what HR does next — it simply provides the pre-filtered results and tools. HR decides the next steps based on their process.

---

## 10. Notifications

### 10.1 Email Notifications
- Candidate: application confirmation with interview link, interview results/status update, vacancy closed notification
- HR: new application received, interview completed (with quick score summary), daily/weekly digest of activity
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

## 12. Candidate Statuses (per vacancy)

1. **Applied** — application submitted, interview link generated, waiting for candidate to start
2. **Interview In Progress** — candidate has started the AI interview (chat or video session is active)
3. **Interview Completed** — AI interview done, scores generated
4. **Reviewing** — HR is reviewing the candidate
5. **Shortlisted** — HR marked as potential hire
6. **Rejected** — HR decided not to proceed
7. **Expired** — vacancy was closed before the candidate completed the interview

---

## 13. Security & Data

- Candidate data is private and isolated per company
- CV files stored securely (encrypted at rest)
- Interview recordings stored securely with access controls (Meet mode only)
- GDPR considerations: candidates can request data deletion
- Authentication: email/password + social login (Google)
- Role-based access control (Admin, HR, Candidate)

### 13.1 Anonymous Access & Account Binding
- Candidates can apply to vacancies and complete interviews without creating an account
- Interview links contain a UUID token that serves as an unguessable credential, granting access to that specific interview session only
- Chat mode sessions use the interview token for resumption — candidate can close the browser and reopen the link to continue
- Account creation is suggested after interview completion (on the "Thank you" screen and in the confirmation email)
- When a candidate creates an account, the system automatically binds their previous applications and interviews:
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

### 14.3 Company Profile Setup

1. Upload company logo
2. Write company description (shown on public job board)
3. Add company website URL
4. Configure default settings:
   - Preferred interview language (EN/RU)
   - Default interview duration
   - Default screening mode (Chat or Meet)
   - Notification preferences

### 14.4 Inviting HR Users

1. Company admin goes to "Team" section
2. Invites HR managers by email
3. Invited HR receives an email with a sign-up link
4. HR creates their account and is automatically linked to the company
5. Company admin can manage HR permissions (activate/deactivate)

### 14.5 Creating First Vacancy

1. After onboarding, the system guides the HR to create their first vacancy
2. A brief tutorial/wizard walks through vacancy creation steps
3. HR selects screening mode (Chat or Meet)
4. Once published, the vacancy is live and ready to receive candidates

---

## 15. AI Interview Integrity & Anti-Cheating

### 15.1 Identity Verification (Meet mode only)

- Before the interview starts, candidate is asked to show an ID document on camera (optional, configurable by HR)
- System takes a photo of the candidate at the start of the interview
- Photo is stored and available for HR to compare with CV photo (if provided)

### 15.2 Behavior Monitoring During Interview (Meet mode only)

- **Face presence detection** — AI monitors that a face is visible on camera throughout the interview. If the candidate disappears for an extended period, a warning is issued
- **Multiple faces detection** — if more than one person is detected on camera, AI flags it
- **Eye tracking / gaze detection** — AI monitors if the candidate is frequently looking away from the screen (possible sign of reading from notes). This is logged as a note, not an automatic disqualification
- **Audio anomaly detection** — AI detects if another voice is heard or if the candidate appears to be receiving prompts from someone else

### 15.3 Content-Based Cheating Detection (both modes)

- **Response consistency** — AI cross-references interview answers with CV claims (if CV was uploaded). Inconsistencies are flagged (e.g., claims 5 years of React experience but can't answer basic questions)
- **Scripted answer detection** — AI analyzes response patterns. If answers sound overly rehearsed or read aloud (unnatural pacing, no pauses), it's noted
- **AI-generated answer detection** — if candidate appears to be using ChatGPT or similar tools, this is flagged
- **Response timing analysis (Chat mode)** — suspiciously fast or slow replies may indicate copy-paste from external tools or AI-generated answers

### 15.4 Integrity Report

- After each interview, an integrity section is included in the candidate's evaluation
- Flags are shown to HR with severity levels: info, warning, critical
- HR makes the final decision — flags are informational, not automatic rejections
- Examples of flags:
  - "Candidate looked away from screen frequently (12 times)" (Meet only)
  - "Second person briefly detected at 04:23" (Meet only)
  - "CV states 5 years Python experience but struggled with basic questions" (both modes)
  - "Multiple responses appeared copy-pasted (avg response time: 2 seconds for 200+ word answers)" (Chat only)

---

## 16. Edge Cases & Error Handling

### 16.1 Mid-Interview Disconnect (Meet mode)
- If the candidate's connection drops, the room stays alive for a reconnection window (default: 5 minutes)
- The AI agent pauses and waits for the candidate to rejoin
- If the candidate reconnects within the window, the interview resumes from where it left off
- If the candidate does not reconnect, the interview is completed with partial data and a note indicating disconnection

### 16.2 Browser Close Mid-Chat (Chat mode)
- Chat history is persisted server-side
- Candidate reopens the interview link and sees their full conversation history
- The interview continues from where it left off
- If no messages are sent for the idle timeout period (default: 24 hours), the interview is auto-completed with partial data and a note indicating abandonment

### 16.3 Vacancy Closed During Active Interview
- **Interview not started (pending):** link becomes invalid, candidate sees "This vacancy is no longer accepting applications"
- **Interview in progress:** allowed to complete normally, results are evaluated and saved

### 16.4 Interview Retry Policy
- One interview per application by default
- If a candidate's interview was abandoned (started but not finished), HR can manually reset the interview to generate a new link for the same application
- Candidates cannot self-retry; this prevents gaming the system by repeatedly taking the same interview
- Completed interviews cannot be reset

### 16.5 AI Service Unavailable
- Before connecting the candidate, the system performs a health check on the AI service (OpenAI for chat, LiveKit agent for meet)
- If the service is unavailable, the candidate sees: "Our interviewer is temporarily unavailable. Please try again in a few minutes."
- System notifies the admin of the outage
- The interview status remains "pending" so the candidate can try again later

### 16.6 Concurrent Interviews
- Each candidate's interview gets its own independent session (chat thread or video room)
- Multiple candidates can interview simultaneously for the same vacancy
- No scheduling conflicts since there is no scheduling
- System may enforce per-vacancy concurrency limits to prevent overload (configurable)

### 16.7 Link Sharing Prevention
- **Meet mode:** LiveKit room token is bound to the candidate. Room has max 2 participants (candidate + AI agent). If someone else tries to join with the same link while the session is active, they see "Interview session is already in use."
- **Chat mode:** interview token is unique per application. If a session is already active from another browser, the new session takes over (last-writer-wins) to handle legitimate tab switches

### 16.8 CV Processing Timing
- CV parsing is asynchronous (Celery task). If the candidate starts the interview before CV processing completes:
  - AI proceeds without CV context
  - AI focuses on vacancy-specific questions only
  - Once CV processing completes, the data is available for the evaluation step (even if not used during the live interview)

### 16.9 Vacancy Closure & Interview Cleanup
- When a vacancy is closed, a background task processes all pending (not started) interviews for that vacancy
- Pending interviews have their status set to "Expired"
- Corresponding applications are also set to "Expired"
- Candidate receives an email: "The vacancy you applied for has been closed."
- In-progress interviews are allowed to complete before cleanup

---

## 17. Future Considerations (Post-MVP)

- Mobile applications (iOS, Android)
- Additional languages beyond EN/RU
- Integration with external ATS (Applicant Tracking Systems)
- Integration with job boards (LinkedIn, Indeed, HH.ru)
- Advanced analytics and reporting for companies
- Voice-only interview mode (audio without video)
- Code editor integration for technical chat interviews
- Candidate feedback on AI interview experience
- Automated reference checking
- Skill assessment tests (coding challenges, personality tests)
- White-label option for enterprise clients
