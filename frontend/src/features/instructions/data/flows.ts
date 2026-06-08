/**
 * Guide content for the "How it works" page.
 *
 * Each flow groups a sequence of numbered steps, every step backed by a real
 * screenshot captured from the running app (served from /public/guide).
 * Copy lives here (English) rather than the i18n bundles — this is long-form
 * documentation, not chrome, and is intentionally kept in one editable place.
 */

export interface GuideStep {
  /** Short imperative title, e.g. "Open the Vacancies page". */
  title: string
  /** One or two sentences explaining what the user does and sees. */
  description: string
  /** Public path to the screenshot, e.g. /guide/01-vacancies-list.png */
  image: string
  /** Accessible alt text describing the screenshot. */
  imageAlt: string
}

export interface GuideFlow {
  /** Stable anchor id used by the table of contents. */
  id: string
  /** PrimeIcons class for the section badge. */
  icon: string
  /** Section heading. */
  title: string
  /** Who performs this flow. */
  audience: 'hr' | 'candidate'
  /** One-line summary shown under the heading. */
  summary: string
  steps: GuideStep[]
}

export const GUIDE_FLOWS: GuideFlow[] = [
  {
    id: 'create-vacancy',
    icon: 'pi pi-briefcase',
    title: 'Create a vacancy',
    audience: 'hr',
    summary: 'Set up the role and candidate requirements that everything else is built on.',
    steps: [
      {
        title: 'Open the Vacancies page',
        description:
          'From the sidebar go to Vacancies. This lists every role with its status and applicant counts. Click “New Vacancy” to start a screening funnel.',
        image: '/guide/01-vacancies-list.png',
        imageAlt: 'Vacancies list with the New Vacancy button',
      },
      {
        title: 'Fill in the vacancy details',
        description:
          'In the Basic Info tab enter the title, description, requirements and responsibilities. You can write them yourself or use “Generate with AI”. Other tabs let you set company info and candidate filters.',
        image: '/guide/02-create-form.png',
        imageAlt: 'Create screening funnel form with title and description',
      },
      {
        title: 'Save and open the vacancy',
        description:
          'Saving creates the vacancy as a draft and opens its detail page. From here you configure pre-screening, the interview, and publishing.',
        image: '/guide/03-vacancy-detail.png',
        imageAlt: 'Vacancy detail page showing job info and section rail',
      },
    ],
  },
  {
    id: 'setup-prescreen',
    icon: 'pi pi-comments',
    title: 'Set up pre-screening',
    audience: 'hr',
    summary: 'Tell the AI what to probe for and how to score every applicant.',
    steps: [
      {
        title: 'Write the AI instructions',
        description:
          'Open the Pre-screening section. Pre-screening is always on — every applicant chats with the AI after applying. Pick the screening language and tell the AI what to focus on (topics, red flags, tone, or sample questions).',
        image: '/guide/04-prescreen-instructions.png',
        imageAlt: 'Pre-screening AI instructions and screening language',
      },
      {
        title: 'Review the scoring criteria',
        description:
          'Below the instructions, the AI scores answers against weighted criteria. Sensible defaults (Technical Skills, Communication, Problem Solving, Cultural Fit, Experience) are provided, and you can add or re-weight your own.',
        image: '/guide/05-prescreen-criteria.png',
        imageAlt: 'Pre-screening scoring criteria list with weights',
      },
    ],
  },
  {
    id: 'setup-interview',
    icon: 'pi pi-video',
    title: 'Set up the AI interview',
    audience: 'hr',
    summary: 'Add an optional deeper interview for candidates who pass pre-screening.',
    steps: [
      {
        title: 'Enable the second-step interview',
        description:
          'In the Settings section turn on “Second-step AI Interview”. This unlocks a deeper interview that strong candidates are invited to after pre-screening.',
        image: '/guide/06-interview-enable.png',
        imageAlt: 'Settings section with the Second-step AI Interview toggle',
      },
      {
        title: 'Configure the interview',
        description:
          'Open the Interview section to set the mode (video or chat), duration, and AI instructions for what the interviewer should ask and verify.',
        image: '/guide/07-interview-instructions.png',
        imageAlt: 'Interview mode, duration and AI instructions',
      },
      {
        title: 'Define the interview criteria',
        description:
          'Add the weighted criteria used to score the interview. The combined CV, pre-screen and interview scores produce each candidate’s overall ranking.',
        image: '/guide/08-interview-criteria.png',
        imageAlt: 'Interview scoring criteria list',
      },
    ],
  },
  {
    id: 'candidate-results',
    icon: 'pi pi-chart-bar',
    title: 'Review candidate results',
    audience: 'hr',
    summary: 'See each applicant’s scores, answers and an AI recommendation in one place.',
    steps: [
      {
        title: 'Open the Candidates board',
        description:
          'Go to Candidates to see applicants on a pipeline board — Applied, Prescanned, Interviewed, Shortlisted — each card showing CV match and pre-screen scores.',
        image: '/guide/09-candidates-list.png',
        imageAlt: 'Candidates kanban board with pipeline columns',
      },
      {
        title: 'Open a candidate',
        description:
          'A candidate’s page opens on Overview with a score card breaking down the overall score into CV match and pre-screening.',
        image: '/guide/10-candidate-overview.png',
        imageAlt: 'Candidate overview with overall score card',
      },
      {
        title: 'Read the pre-screening results',
        description:
          'The Pre-screening tab shows the AI’s scores and summary — recommendation, strengths, risks and a suggested next step — plus the full chat transcript.',
        image: '/guide/11-candidate-prescreen.png',
        imageAlt: 'Pre-screening scores, recommendation, strengths and risks',
      },
      {
        title: 'Check the overall analysis',
        description:
          'The Analysis tab combines CV, pre-screen and interview into one verdict with a clear recommendation, so you can decide who to move forward.',
        image: '/guide/12-candidate-analysis.png',
        imageAlt: 'Combined analysis with overall recommendation',
      },
    ],
  },
  {
    id: 'pass-prescreen',
    icon: 'pi pi-send',
    title: 'How a candidate passes pre-screening',
    audience: 'candidate',
    summary: 'What the applicant sees — no account required, everything works from one link.',
    steps: [
      {
        title: 'Apply via the link',
        description:
          'The candidate opens the public apply link, enters their name, email and phone, and optionally uploads a CV. No sign-up is required.',
        image: '/guide/13-apply-form.png',
        imageAlt: 'Candidate application form',
      },
      {
        title: 'Start the pre-screen',
        description:
          'After submitting they see a confirmation and can start the AI pre-screening right away, or use the saved link (also sent by email) to finish later.',
        image: '/guide/14-apply-ready.png',
        imageAlt: 'Pre-screening ready screen with start button',
      },
      {
        title: 'Chat with the AI',
        description:
          'The candidate answers the AI’s questions by text or voice. The conversation adapts to their answers, and responses are scored automatically in the background.',
        image: '/guide/15-prescreen-chat.png',
        imageAlt: 'Candidate pre-screening chat with the AI',
      },
      {
        title: 'Finish',
        description:
          'When the chat ends the candidate sees a completion screen and their responses are sent for review. Scored results appear immediately on your Candidates board.',
        image: '/guide/16-prescreen-done.png',
        imageAlt: 'Pre-screening completed screen',
      },
    ],
  },
]
