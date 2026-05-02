import type { Router } from 'vue-router'

type AnalyticsValue = string | number | boolean | null | undefined
type AnalyticsParams = Record<string, AnalyticsValue>

declare global {
  interface Window {
    dataLayer?: IArguments[]
    gtag?: {
      (...args: unknown[]): void
      q?: IArguments[]
    }
  }
}

const measurementId = import.meta.env.VITE_GA_MEASUREMENT_ID as string | undefined
let initialized = false
let actionTrackingInstalled = false
let lastTrackedPath = ''

function isEnabled(): boolean {
  return Boolean(measurementId)
}

function loadGoogleAnalyticsScript(id: string): void {
  if (document.querySelector(`script[data-ga-id="${id}"]`)) return

  const script = document.createElement('script')
  script.async = true
  script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(id)}`
  script.dataset.gaId = id
  document.head.appendChild(script)
}

function trackPageView(path: string, title: string): void {
  if (!isEnabled() || !window.gtag || path === lastTrackedPath || !measurementId) return

  lastTrackedPath = path
  window.gtag('event', 'page_view', {
    send_to: measurementId,
    page_location: window.location.href,
    page_path: path,
    page_title: title,
  })
}

function compactParams(params: AnalyticsParams): Record<string, string | number | boolean> {
  return Object.entries(params).reduce<Record<string, string | number | boolean>>(
    (result, [key, value]) => {
      if (value === undefined || value === null || value === '') return result
      result[key] = value
      return result
    },
    {},
  )
}

function safeAttribute(value: string | null | undefined, maxLength = 80): string | undefined {
  const normalized = value?.trim()
  if (!normalized) return undefined

  return normalized.replace(/\s+/g, ' ').slice(0, maxLength)
}

function safeEventName(value: string | null | undefined, fallback: string): string {
  const normalized = value
    ?.trim()
    .toLowerCase()
    .replace(/[^a-z0-9_]+/g, '_')
    .replace(/^_+|_+$/g, '')
    .slice(0, 40)

  return normalized && /^[a-z]/.test(normalized) ? normalized : fallback
}

function currentPagePath(): string {
  return `${window.location.pathname}${window.location.search}${window.location.hash}`
}

function getActionElement(target: EventTarget | null): HTMLElement | null {
  if (!(target instanceof Element)) return null

  return target.closest<HTMLElement>(
    '[data-analytics-event], button, a, [role="button"], input[type="button"], input[type="submit"]',
  )
}

function getActionLabel(element: HTMLElement): string | undefined {
  return (
    safeAttribute(element.dataset.analyticsLabel) ??
    safeAttribute(element.getAttribute('aria-label')) ??
    safeAttribute(element.getAttribute('title'))
  )
}

function getElementType(element: HTMLElement): string | undefined {
  if (element instanceof HTMLButtonElement || element instanceof HTMLInputElement) {
    return safeAttribute(element.type)
  }

  return undefined
}

function getLinkTarget(element: HTMLElement): string | undefined {
  if (!(element instanceof HTMLAnchorElement) || !element.href) return undefined

  try {
    const url = new URL(element.href)
    return url.origin === window.location.origin ? url.pathname : url.hostname
  } catch {
    return undefined
  }
}

function getClickEventName(element: HTMLElement): string {
  const customEvent = element.dataset.analyticsEvent
  if (customEvent) return safeEventName(customEvent, 'app_click')

  return element instanceof HTMLAnchorElement ? 'app_link_click' : 'app_button_click'
}

function trackClick(event: MouseEvent): void {
  const element = getActionElement(event.target)
  if (!element) return

  trackAnalyticsEvent(getClickEventName(element), {
    page_path: currentPagePath(),
    element_tag: element.tagName.toLowerCase(),
    element_id: safeAttribute(element.id),
    element_role: safeAttribute(element.getAttribute('role')),
    element_type: getElementType(element),
    element_label: getActionLabel(element),
    link_target: getLinkTarget(element),
  })
}

function trackSubmit(event: SubmitEvent): void {
  if (!(event.target instanceof HTMLFormElement)) return

  const form = event.target
  trackAnalyticsEvent(safeEventName(form.dataset.analyticsEvent, 'app_form_submit'), {
    page_path: currentPagePath(),
    element_tag: 'form',
    element_id: safeAttribute(form.id),
    element_label: getActionLabel(form),
  })
}

function installActionTracking(): void {
  if (actionTrackingInstalled) return

  actionTrackingInstalled = true
  document.addEventListener('click', trackClick, { capture: true })
  document.addEventListener('submit', trackSubmit, { capture: true })
}

export function trackAnalyticsEvent(eventName: string, params: AnalyticsParams = {}): void {
  if (!isEnabled() || !window.gtag || !measurementId) return

  window.gtag('event', safeEventName(eventName, 'app_event'), {
    send_to: measurementId,
    ...compactParams(params),
  })
}

export function initializeGoogleAnalytics(router: Router): void {
  if (!isEnabled() || initialized || !measurementId) return

  initialized = true
  window.dataLayer = window.dataLayer || []
  window.gtag = function gtag() {
    // Google gtag expects the native arguments object, not a rest-args array.
    // eslint-disable-next-line prefer-rest-params
    window.dataLayer?.push(arguments)
  }

  window.gtag('js', new Date())
  window.gtag('config', measurementId, { send_page_view: false })
  loadGoogleAnalyticsScript(measurementId)
  installActionTracking()

  router.afterEach((to) => {
    trackPageView(to.fullPath, document.title)
  })

  void router.isReady().then(() => {
    trackPageView(router.currentRoute.value.fullPath, document.title)
  })
}
