import { useI18n } from 'vue-i18n'
import { computed } from 'vue'
import type { Vacancy } from '../types/vacancy.types'

export function useEmploymentLabels() {
  const { t } = useI18n()
  return computed<Record<string, string>>(() => ({
    full_time: t('vacancies.employment.fullTime'),
    part_time: t('vacancies.employment.partTime'),
    contract: t('vacancies.employment.contract'),
    internship: t('vacancies.employment.internship'),
  }))
}

export function useExperienceLabels() {
  const { t } = useI18n()
  return computed<Record<string, string>>(() => ({
    junior: t('vacancies.experience.junior'),
    middle: t('vacancies.experience.middle'),
    senior: t('vacancies.experience.senior'),
    lead: t('vacancies.experience.lead'),
    director: t('vacancies.experience.director'),
  }))
}

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

export function formatSalaryRange(vacancy: Vacancy, t: (key: string, params?: Record<string, unknown>) => string): string {
  const { salaryMin, salaryMax, salaryCurrency } = vacancy
  if (!salaryMin && !salaryMax) return t('vacancies.overview.salaryNotSpecified')
  if (salaryMin && salaryMax) {
    return t('vacancies.overview.salaryRange', { min: formatMoney(salaryMin), max: formatMoney(salaryMax), currency: salaryCurrency })
  }
  if (salaryMin) return t('vacancies.overview.salaryFrom', { amount: formatMoney(salaryMin), currency: salaryCurrency })
  return t('vacancies.overview.salaryUpTo', { amount: formatMoney(salaryMax!), currency: salaryCurrency })
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString()
}
