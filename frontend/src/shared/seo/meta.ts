import { getLocale } from '@/shared/i18n'

const DEFAULT_SITE_URL = 'https://prescreen-app.com'
const DEFAULT_TITLE = 'PreScreen AI - AI-Powered Candidate Screening'
const DEFAULT_DESCRIPTION =
  'Screen candidates automatically with AI interviews, vacancy prescreening, and multilingual hiring workflows.'
const DEFAULT_IMAGE_PATH = '/og-image.png'

export interface SeoMetaInput {
  title?: string
  description?: string
  path?: string
  canonicalUrl?: string
  image?: string
  type?: 'website' | 'article' | 'profile'
  robots?: string
}

export function getSiteUrl(): string {
  const configured = import.meta.env.VITE_SITE_URL
  if (configured) return configured.replace(/\/$/, '')
  if (typeof window !== 'undefined' && window.location.origin) return window.location.origin
  return DEFAULT_SITE_URL
}

export function absoluteUrl(pathOrUrl: string): string {
  if (/^https?:\/\//i.test(pathOrUrl)) return pathOrUrl
  const path = pathOrUrl.startsWith('/') ? pathOrUrl : `/${pathOrUrl}`
  return `${getSiteUrl()}${path}`
}

export function stripHtml(value: string | null | undefined): string {
  if (!value) return ''
  return value
    .replace(/<[^>]*>/g, ' ')
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/\s+/g, ' ')
    .trim()
}

export function truncate(value: string, maxLength: number): string {
  if (value.length <= maxLength) return value
  const trimmed = value.slice(0, Math.max(0, maxLength - 3)).trimEnd()
  return `${trimmed}...`
}

export function setSeoMeta(input: SeoMetaInput = {}): void {
  if (typeof document === 'undefined') return

  const title = input.title ?? DEFAULT_TITLE
  const description = truncate(input.description ?? DEFAULT_DESCRIPTION, 180)
  const canonicalUrl = input.canonicalUrl ?? absoluteUrl(input.path ?? window.location.pathname)
  const image = absoluteUrl(input.image ?? DEFAULT_IMAGE_PATH)
  const robots = input.robots ?? 'index, follow'
  const imageAlt = `${title} social preview`

  document.title = title
  upsertMeta('name', 'title', title)
  upsertMeta('name', 'description', description)
  upsertMeta('name', 'robots', robots)

  upsertMeta('property', 'og:type', input.type ?? 'website')
  upsertMeta('property', 'og:url', canonicalUrl)
  upsertMeta('property', 'og:title', title)
  upsertMeta('property', 'og:description', description)
  upsertMeta('property', 'og:image', image)
  upsertMeta('property', 'og:image:alt', imageAlt)
  upsertMeta('property', 'og:image:width', '1200')
  upsertMeta('property', 'og:image:height', '630')
  upsertMeta('property', 'og:site_name', 'PreScreen AI')
  upsertMeta('property', 'og:locale', toOpenGraphLocale(getLocale()))

  upsertMeta('name', 'twitter:card', 'summary_large_image')
  upsertMeta('name', 'twitter:url', canonicalUrl)
  upsertMeta('name', 'twitter:title', title)
  upsertMeta('name', 'twitter:description', description)
  upsertMeta('name', 'twitter:image', image)
  upsertMeta('name', 'twitter:image:alt', imageAlt)
  upsertCanonical(canonicalUrl)
}

export function setJsonLd(id: string, data: unknown | null): void {
  if (typeof document === 'undefined') return
  const current = document.getElementById(id)
  if (!data) {
    current?.remove()
    return
  }

  const script = (current as HTMLScriptElement | null) ?? document.createElement('script')
  script.id = id
  script.type = 'application/ld+json'
  script.textContent = JSON.stringify(data)
  if (!current) document.head.append(script)
}

function upsertMeta(attribute: 'name' | 'property', key: string, content: string): void {
  let element = document.head.querySelector<HTMLMetaElement>(`meta[${attribute}="${key}"]`)
  if (!element) {
    element = document.createElement('meta')
    element.setAttribute(attribute, key)
    document.head.append(element)
  }
  element.content = content
}

function upsertCanonical(href: string): void {
  let element = document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]')
  if (!element) {
    element = document.createElement('link')
    element.rel = 'canonical'
    document.head.append(element)
  }
  element.href = href
}

function toOpenGraphLocale(locale: string): string {
  const localeMap: Record<string, string> = {
    en: 'en_US',
    ru: 'ru_RU',
    uz: 'uz_UZ',
    kk: 'kk_KZ',
    tr: 'tr_TR',
    ar: 'ar_SA',
    es: 'es_ES',
    fr: 'fr_FR',
    de: 'de_DE',
    uk: 'uk_UA',
  }
  return localeMap[locale] ?? 'en_US'
}
