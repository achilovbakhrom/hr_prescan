import type { GuideText } from '../guide.types'

const en: GuideText = {
  title: 'How it works',
  subtitle:
    'A step-by-step walkthrough of PreScreen AI — from posting a role to reviewing scored candidates, plus what applicants experience. Click any screenshot to view it full size.',
  onThisPage: 'On this page',
  forHr: 'For HR',
  forCandidates: 'For candidates',
  flows: {
    'create-vacancy': {
      title: 'Create a vacancy',
      summary: 'Set up the role and candidate requirements that everything else is built on.',
      steps: [
        {
          title: 'Open the Vacancies page',
          description:
            'From the sidebar go to Vacancies. This lists every role with its status and applicant counts. Click “New Vacancy” to start a screening funnel.',
          alt: 'Vacancies list with the New Vacancy button',
        },
        {
          title: 'Fill in the vacancy details',
          description:
            'In the Basic Info tab enter the title, description, requirements and responsibilities. You can write them yourself or use “Generate with AI”.',
          alt: 'Create screening funnel form with title and description',
        },
        {
          title: 'Save and open the vacancy',
          description:
            'Saving creates the vacancy as a draft and opens its detail page, where you configure pre-screening, the interview, and publishing.',
          alt: 'Vacancy detail page showing job info and section rail',
        },
      ],
    },
    'setup-prescreen': {
      title: 'Set up pre-screening',
      summary: 'Tell the AI what to probe for and how to score every applicant.',
      steps: [
        {
          title: 'Write the AI instructions',
          description:
            'Open the Pre-screening section. Every applicant chats with the AI after applying. Pick the screening language and tell the AI what to focus on.',
          alt: 'Pre-screening AI instructions and screening language',
        },
        {
          title: 'Review the scoring criteria',
          description:
            'The AI scores answers against weighted criteria. Sensible defaults are provided, and you can add or re-weight your own.',
          alt: 'Pre-screening scoring criteria list with weights',
        },
      ],
    },
    'setup-interview': {
      title: 'Set up the AI interview',
      summary: 'Add an optional deeper interview for candidates who pass pre-screening.',
      steps: [
        {
          title: 'Enable the second-step interview',
          description:
            'In the Settings section turn on “Second-step AI Interview”. This unlocks a deeper interview for strong candidates.',
          alt: 'Settings section with the Second-step AI Interview toggle',
        },
        {
          title: 'Configure the interview',
          description:
            'Open the Interview section to set the mode (video or chat), duration, and AI instructions for what to ask and verify.',
          alt: 'Interview mode, duration and AI instructions',
        },
        {
          title: 'Define the interview criteria',
          description:
            'Add the weighted criteria used to score the interview. CV, pre-screen and interview scores combine into each candidate’s overall ranking.',
          alt: 'Interview scoring criteria list',
        },
      ],
    },
    'candidate-results': {
      title: 'Review candidate results',
      summary: 'See each applicant’s scores, answers and an AI recommendation in one place.',
      steps: [
        {
          title: 'Open the Candidates board',
          description:
            'Go to Candidates to see applicants on a pipeline board — Applied, Prescanned, Interviewed, Shortlisted — with CV and pre-screen scores.',
          alt: 'Candidates kanban board with pipeline columns',
        },
        {
          title: 'Open a candidate',
          description:
            'A candidate’s page opens on Overview with a score card breaking the overall score into CV match and pre-screening.',
          alt: 'Candidate overview with overall score card',
        },
        {
          title: 'Read the pre-screening results',
          description:
            'The Pre-screening tab shows the AI’s scores and summary — recommendation, strengths, risks, next step — plus the full chat transcript.',
          alt: 'Pre-screening scores, recommendation, strengths and risks',
        },
        {
          title: 'Check the overall analysis',
          description:
            'The Analysis tab combines CV, pre-screen and interview into one verdict with a clear recommendation, so you can decide who to move forward.',
          alt: 'Combined analysis with overall recommendation',
        },
      ],
    },
    'pass-prescreen': {
      title: 'How a candidate passes pre-screening',
      summary: 'What the applicant sees — no account required, everything works from one link.',
      steps: [
        {
          title: 'Apply via the link',
          description:
            'The candidate opens the public apply link, enters their name, email and phone, and optionally uploads a CV. No sign-up is required.',
          alt: 'Candidate application form',
        },
        {
          title: 'Start the pre-screen',
          description:
            'After submitting they see a confirmation and can start the AI pre-screening right away, or use the saved link to finish later.',
          alt: 'Pre-screening ready screen with start button',
        },
        {
          title: 'Chat with the AI',
          description:
            'The candidate answers the AI’s questions by text or voice. The conversation adapts, and responses are scored automatically in the background.',
          alt: 'Candidate pre-screening chat with the AI',
        },
        {
          title: 'Finish',
          description:
            'When the chat ends the candidate sees a completion screen and their responses are sent for review. Scored results appear on your Candidates board.',
          alt: 'Pre-screening completed screen',
        },
      ],
    },
    'ai-assistant': {
      title: 'Do it with the AI assistant',
      summary:
        'Ask in plain language — the assistant finds candidates, drafts vacancies and analyzes your funnel.',
      steps: [
        {
          title: 'Open the assistant',
          description:
            'Click “Ask AI” to open the HR assistant. The quick-action cards show what it can do — find candidates, create a vacancy, work with vacancies, or analyze your hiring funnel.',
          alt: 'AI assistant with quick-action cards',
        },
        {
          title: 'Ask in plain language',
          description:
            'Type a request and the assistant does the work: it reads your data, performs actions and replies with a clear answer and the next step.',
          alt: 'AI assistant answering an HR question',
        },
      ],
    },
  },
}

export default en
