import type { Company } from '@/features/companies/types/company.types'
import { absoluteUrl, setJsonLd, setSeoMeta, stripHtml, truncate } from '@/shared/seo/meta'
import type { Vacancy } from '../types/vacancy.types'

interface VacancyWithCompany extends Vacancy {
  company?: Company
  companyName?: string | null
}

interface VacancySeoOptions {
  noindex?: boolean
}

const JOB_POSTING_ID = 'job-posting'

export function applyPublicVacancySeo(
  vacancy: VacancyWithCompany,
  options: VacancySeoOptions,
): void {
  const seo = buildPublicVacancySeoMeta(vacancy, options)
  setSeoMeta(seo)

  if (options.noindex) {
    setJsonLd(JOB_POSTING_ID, null)
    return
  }

  const jobPosting = buildPublicVacancyJsonLd(vacancy)
  setJsonLd(JOB_POSTING_ID, jobPosting)
}

export function clearPublicVacancySeo(): void {
  setJsonLd(JOB_POSTING_ID, null)
}

export function buildPublicVacancySeoMeta(
  vacancy: VacancyWithCompany,
  options: VacancySeoOptions,
): {
  title: string
  description: string
  canonicalUrl: string
  path: string
  type: 'article'
  robots: string
} {
  const companyName = vacancy.company?.name ?? vacancy.companyName ?? 'PreScreen AI'
  const path = `/jobs/${vacancy.id}`

  return {
    title: `${vacancy.title} at ${companyName}`,
    description: buildDescription(vacancy),
    canonicalUrl: absoluteUrl(path),
    path,
    type: 'article',
    robots: options.noindex ? 'noindex, follow' : 'index, follow',
  }
}

export function buildPublicVacancyJsonLd(
  vacancy: VacancyWithCompany,
): Record<string, unknown> | null {
  const companyName = vacancy.company?.name ?? vacancy.companyName ?? 'PreScreen AI'
  return buildJobPosting(vacancy, companyName, absoluteUrl(`/jobs/${vacancy.id}`))
}

function buildDescription(vacancy: Vacancy): string {
  const primary = stripHtml(vacancy.description)
  if (primary) return truncate(primary, 180)

  const fallback = [vacancy.title, vacancy.location, vacancy.employmentType]
    .filter(Boolean)
    .join(' - ')
  return truncate(`Apply for ${fallback} with PreScreen AI.`, 180)
}

function buildJobPosting(
  vacancy: VacancyWithCompany,
  companyName: string,
  canonicalUrl: string,
): Record<string, unknown> | null {
  const location = parseLocation(vacancy.location)
  if (!hasHiringOrganization(vacancy) || (!vacancy.isRemote && !location)) return null

  const organization: Record<string, unknown> = {
    '@type': 'Organization',
    name: companyName,
  }

  const logo = vacancy.company?.logo ?? vacancy.companyLogo
  if (logo) organization.logo = absoluteUrl(logo)
  if (vacancy.company?.website) organization.sameAs = vacancy.company.website

  const jobPosting: Record<string, unknown> = {
    '@context': 'https://schema.org',
    '@type': 'JobPosting',
    title: vacancy.title,
    description: buildStructuredDescription(vacancy),
    datePosted: vacancy.createdAt,
    employmentType: vacancy.employmentType.toUpperCase(),
    hiringOrganization: organization,
    directApply: vacancy.canApply !== false,
    url: canonicalUrl,
  }

  if (vacancy.isRemote) {
    jobPosting.jobLocationType = 'TELECOMMUTE'
  } else if (location) {
    jobPosting.jobLocation = {
      '@type': 'Place',
      address: {
        '@type': 'PostalAddress',
        addressLocality: location.locality,
        addressCountry: location.country,
      },
    }
  }

  return jobPosting
}

function hasHiringOrganization(vacancy: VacancyWithCompany): boolean {
  return Boolean(vacancy.company?.name || vacancy.companyName)
}

function buildStructuredDescription(vacancy: Vacancy): string {
  return (
    [vacancy.description, vacancy.responsibilities, vacancy.requirements]
      .map((section) => stripHtml(section))
      .filter(Boolean)
      .join('\n\n') || buildDescription(vacancy)
  )
}

function parseLocation(location: string): { locality: string; country: string } | null {
  const parts = location
    .split(',')
    .map((part) => part.trim())
    .filter(Boolean)

  if (parts.length < 2) return null
  return {
    locality: parts.slice(0, -1).join(', '),
    country: parts.at(-1) ?? '',
  }
}
