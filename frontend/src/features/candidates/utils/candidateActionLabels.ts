import type { Application, ApplicationStatus } from '../types/candidate.types'

export type CandidateTranslate = (key: string) => string
export type ScoreField = 'match_score' | 'prescanning_score' | 'interview_score'

export function statusLabel(t: CandidateTranslate, status: ApplicationStatus): string {
  return t(`candidates.status.${status}`)
}

export function scoreFieldLabel(t: CandidateTranslate, field: string): string {
  if (field === 'match_score') return t('candidates.scoreFields.cvMatch')
  if (field === 'prescanning_score') return t('candidates.scoreFields.prescan')
  return t('candidates.scoreFields.interview')
}

export function scoreValue(candidate: Application, field: string): number | null {
  if (field === 'match_score') return candidate.matchScore
  if (field === 'prescanning_score') return candidate.prescanningScore
  if (field === 'interview_score') return candidate.interviewScore
  return null
}

export function olderThanDays(createdAt: string, days: number): boolean {
  const created = Date.parse(createdAt)
  if (Number.isNaN(created)) return false
  return created < Date.now() - days * 24 * 60 * 60 * 1000
}
