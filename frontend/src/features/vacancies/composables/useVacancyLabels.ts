import type { Vacancy } from '../types/vacancy.types'

export const EMPLOYMENT_LABELS: Record<string, string> = {
  full_time: 'Full Time',
  part_time: 'Part Time',
  contract: 'Contract',
  internship: 'Internship',
}

export const EXPERIENCE_LABELS: Record<string, string> = {
  junior: 'Junior',
  middle: 'Middle',
  senior: 'Senior',
  lead: 'Lead',
  director: 'Director',
}

export function formatSalaryRange(vacancy: Vacancy): string {
  const { salaryMin, salaryMax, salaryCurrency } = vacancy
  if (!salaryMin && !salaryMax) return 'Not specified'
  if (salaryMin && salaryMax) {
    return `${salaryMin.toLocaleString()} - ${salaryMax.toLocaleString()} ${salaryCurrency}`
  }
  if (salaryMin) return `From ${salaryMin.toLocaleString()} ${salaryCurrency}`
  return `Up to ${salaryMax?.toLocaleString()} ${salaryCurrency}`
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}
