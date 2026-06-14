/** Types for the localized "How it works" guide. */

export type GuideAudience = 'hr' | 'candidate'

/** Language-independent structure: which steps exist and their screenshot. */
export interface GuideStructStep {
  /** Screenshot base name, e.g. '01-vacancies-list' (served from /guide/<locale>/). */
  image: string
}
export interface GuideStruct {
  id: string
  icon: string
  audience: GuideAudience
  steps: GuideStructStep[]
}

/** Per-locale translated text, keyed by flow id. */
export interface StepText {
  title: string
  description: string
  /** Accessible alt text for the screenshot. */
  alt: string
}
export interface FlowText {
  title: string
  summary: string
  steps: StepText[]
}
export interface GuideText {
  title: string
  subtitle: string
  onThisPage: string
  forHr: string
  forCandidates: string
  flows: Record<string, FlowText>
}

/** Merged, ready-to-render shapes. */
export interface GuideStep {
  title: string
  description: string
  image: string
  /** English screenshot, used as a fallback if the localized one is missing. */
  imageFallback: string
  imageAlt: string
}
export interface GuideFlow {
  id: string
  icon: string
  audience: GuideAudience
  title: string
  summary: string
  steps: GuideStep[]
}
export interface Guide {
  page: {
    title: string
    subtitle: string
    onThisPage: string
    forHr: string
    forCandidates: string
  }
  flows: GuideFlow[]
}
