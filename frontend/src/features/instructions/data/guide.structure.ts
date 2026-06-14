import type { GuideStruct } from './guide.types'

/**
 * Language-independent structure of the guide: the five flows, their icons,
 * audience, and the ordered screenshots for each step. Translated text lives in
 * ./text/<locale>.ts and is merged in by ./guide.ts.
 */
export const GUIDE_STRUCTURE: GuideStruct[] = [
  {
    id: 'create-vacancy',
    icon: 'pi pi-briefcase',
    audience: 'hr',
    steps: [
      { image: '01-vacancies-list' },
      { image: '02-create-form' },
      { image: '03-vacancy-detail' },
    ],
  },
  {
    id: 'setup-prescreen',
    icon: 'pi pi-comments',
    audience: 'hr',
    steps: [{ image: '04-prescreen-instructions' }, { image: '05-prescreen-criteria' }],
  },
  {
    id: 'setup-interview',
    icon: 'pi pi-video',
    audience: 'hr',
    steps: [
      { image: '06-interview-enable' },
      { image: '07-interview-instructions' },
      { image: '08-interview-criteria' },
    ],
  },
  {
    id: 'candidate-results',
    icon: 'pi pi-chart-bar',
    audience: 'hr',
    steps: [
      { image: '09-candidates-list' },
      { image: '10-candidate-overview' },
      { image: '11-candidate-prescreen' },
      { image: '12-candidate-analysis' },
    ],
  },
  {
    id: 'pass-prescreen',
    icon: 'pi pi-send',
    audience: 'candidate',
    steps: [
      { image: '13-apply-form' },
      { image: '14-apply-ready' },
      { image: '15-prescreen-chat' },
      { image: '16-prescreen-done' },
    ],
  },
  {
    id: 'ai-assistant',
    icon: 'pi pi-bolt',
    audience: 'hr',
    steps: [{ image: '17-assistant-open' }, { image: '18-assistant-answer' }],
  },
]
