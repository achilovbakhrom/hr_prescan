# HR PreScan — Business Logic

## 1. Overview

HR PreScan is a multi-tenant SaaS platform that automates the candidate pre-screening process using AI-powered video interviews. When a vacancy receives hundreds of applicants, manually screening each one is time-consuming and inconsistent.

**The core goal of the platform is to help HR pre-filter candidates.** The AI conducts structured video interviews, analyzes CVs, and scores candidates — so HR doesn't have to spend time on every applicant. After reviewing AI results, HR decides what to do with qualified candidates: schedule a full interview, start a direct chat, or take any next step they see fit. The platform handles the screening; HR handles the final decision-making.

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
- Configures AI interview parameters (duration, questions, criteria)
- Reviews candidate scores and interview results
- Filters and sorts candidates by AI scores
- Manages candidate pipeline per vacancy

### 2.3 Candidate
- Can browse public vacancies or access private vacancies via direct link
- Account creation is optional (but allows tracking application status and reusing profile)
- Uploads CV/resume
- Schedules and takes AI video interviews
- Receives notifications about application status

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

- Subscription-based model (monthly/yearly plans)
- Plans differ by limits on:
  - Number of active vacancies
  - Number of AI interviews per month
  - Number of HR users
  - Storage for CVs and interview recordings
- Payment integration (Stripe or similar)
- Trial period for new companies

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

---

## 6. Candidate Application Flow

1. Candidate finds a vacancy (public job board or direct link)
2. Candidate fills in personal details (name, email, phone, etc.)
3. Candidate uploads CV/resume (PDF, DOCX supported)
4. Candidate optionally creates an account (for status tracking and profile reuse)
5. Candidate picks an available time slot for the AI interview from a calendar
6. System creates an interview room link (similar to Google Meet) and adds the event to calendars for both candidate and HR
7. Candidate receives confirmation via email with the interview link and details

---

## 7. AI Interview Process

### 7.1 Pre-Interview: CV Analysis
- When a candidate uploads their CV, AI analyzes it before the interview
- AI extracts: skills, experience, education, languages, job history
- AI compares CV content against vacancy requirements
- AI generates a CV match score
- AI uses CV analysis to tailor interview questions (ask about gaps, verify claimed skills, dig into relevant experience)

### 7.2 Interview Setup
- Interview is conducted in a video room (similar to Google Meet)
- AI agent appears as the interviewer in the room
- Interview duration is configurable by HR per vacancy
- Supported languages: English, Russian (candidate or HR selects)

### 7.3 Interview Question Generation
- AI automatically generates interview questions based on:
  - Vacancy description and required skills
  - Candidate's CV (tailored questions)
  - Evaluation criteria set by HR
- HR can review, edit, add, or remove AI-suggested questions before publishing the vacancy
- Questions cover both fixed categories and custom criteria (see 7.5)

### 7.4 Interview Flow
1. At the scheduled time, candidate joins the video room via the link
2. AI agent greets the candidate and explains the process
3. AI asks questions one by one, listens to responses
4. AI can ask follow-up questions based on answers
5. Interview concludes when all questions are covered or time limit is reached
6. AI thanks the candidate and ends the session

### 7.4.1 HR Silent Observer Mode
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

**Output per candidate:**
- Score for each category (1-10)
- Overall weighted score
- Brief AI summary/notes per category explaining the score
- CV match score (from pre-interview analysis)
- Interview transcript
- Interview recording (video)

---

## 8. Interview Scheduling

- HR does NOT need to define availability windows — AI is always available
- Candidate picks any available time slot from a calendar widget
- Time slots could have limits to avoid overloading the system (configurable)
- Upon booking:
  - A video room link is generated
  - Calendar event is created and sent to:
    - Candidate (email + calendar invite)
    - HR (email + calendar invite, for awareness)
  - Reminders are sent before the interview (e.g., 1 hour, 15 minutes before)

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
- Interview recording playback
- Interview transcript
- HR can add their own notes
- HR can mark candidate status: reviewing, shortlisted, rejected

### 9.4 HR Actions After AI Screening

Once HR reviews AI scores and decides a candidate is worth pursuing, they can:
- **Schedule a full interview** — set up a real (human) interview with the candidate, with calendar integration
- **Start a direct chat** — open a messaging thread with the candidate within the platform
- **Send an email** — contact the candidate via email directly from the platform
- **Reject** — mark the candidate as rejected (with optional reason)

The platform does not dictate what HR does next — it simply provides the pre-filtered results and tools. HR decides the next steps based on their process.

---

## 10. Notifications

### 10.1 Email Notifications
- Candidate: application confirmation, interview scheduled, interview reminder, interview results/status update
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

1. **Applied** — CV uploaded, waiting to schedule interview
2. **Interview Scheduled** — time slot selected, waiting for interview
3. **Interview In Progress** — currently in the AI interview
4. **Interview Completed** — AI interview done, scores generated
5. **Reviewing** — HR is reviewing the candidate
6. **Shortlisted** — HR marked as potential hire
7. **Rejected** — HR decided not to proceed

---

## 13. Security & Data

- Candidate data is private and isolated per company
- CV files stored securely (encrypted at rest)
- Interview recordings stored securely with access controls
- GDPR considerations: candidates can request data deletion
- Authentication: email/password + social login (Google)
- Role-based access control (Admin, HR, Candidate)

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
3. Once published, the vacancy is live and ready to receive candidates

---

## 15. AI Interview Integrity & Anti-Cheating

### 15.1 Identity Verification

- Before the interview starts, candidate is asked to show an ID document on camera (optional, configurable by HR)
- System takes a photo of the candidate at the start of the interview
- Photo is stored and available for HR to compare with CV photo (if provided)

### 15.2 Behavior Monitoring During Interview

- **Face presence detection** — AI monitors that a face is visible on camera throughout the interview. If the candidate disappears for an extended period, a warning is issued
- **Multiple faces detection** — if more than one person is detected on camera, AI flags it
- **Eye tracking / gaze detection** — AI monitors if the candidate is frequently looking away from the screen (possible sign of reading from notes). This is logged as a note, not an automatic disqualification
- **Audio anomaly detection** — AI detects if another voice is heard or if the candidate appears to be receiving prompts from someone else

### 15.3 Content-Based Cheating Detection

- **Response consistency** — AI cross-references interview answers with CV claims. Inconsistencies are flagged (e.g., claims 5 years of React experience but can't answer basic questions)
- **Scripted answer detection** — AI analyzes response patterns. If answers sound overly rehearsed or read aloud (unnatural pacing, no pauses), it's noted
- **AI-generated answer detection** — if candidate appears to be reading answers from ChatGPT or similar tools (long pauses followed by fluent recitation), this is flagged

### 15.4 Integrity Report

- After each interview, an integrity section is included in the candidate's evaluation
- Flags are shown to HR with severity levels: info, warning, critical
- HR makes the final decision — flags are informational, not automatic rejections
- Examples of flags:
  - "Candidate looked away from screen frequently (12 times)"
  - "Second person briefly detected at 04:23"
  - "CV states 5 years Python experience but struggled with basic questions"

---

## 16. Future Considerations (Post-MVP)

- Mobile applications (iOS, Android)
- Additional languages beyond EN/RU
- Integration with external ATS (Applicant Tracking Systems)
- Integration with job boards (LinkedIn, Indeed, HH.ru)
- Advanced analytics and reporting for companies
- AI interview in different formats (text chat, voice-only as alternatives)
- Candidate feedback on AI interview experience
- Automated reference checking
- Skill assessment tests (coding challenges, personality tests)
- White-label option for enterprise clients
