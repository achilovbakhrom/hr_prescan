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

export function formatMoney(amount: number): string {
  return Math.round(amount).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
}

export function formatSalaryRange(vacancy: Vacancy): string {
  const { salaryMin, salaryMax, salaryCurrency } = vacancy
  if (!salaryMin && !salaryMax) return 'Not specified'
  if (salaryMin && salaryMax) {
    return `${formatMoney(salaryMin)} - ${formatMoney(salaryMax)} ${salaryCurrency}`
  }
  if (salaryMin) return `From ${formatMoney(salaryMin)} ${salaryCurrency}`
  return `Up to ${formatMoney(salaryMax!)} ${salaryCurrency}`
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}
