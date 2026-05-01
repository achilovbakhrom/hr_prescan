import type { Router } from 'vue-router'

declare global {
  interface Window {
    dataLayer?: unknown[]
    gtag?: (...args: unknown[]) => void
  }
}

const measurementId = import.meta.env.VITE_GA_MEASUREMENT_ID as string | undefined
let initialized = false
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
  if (!isEnabled() || !window.gtag || path === lastTrackedPath) return

  lastTrackedPath = path
  window.gtag('event', 'page_view', {
    page_path: path,
    page_title: title,
  })
}

export function initializeGoogleAnalytics(router: Router): void {
  if (!isEnabled() || initialized || !measurementId) return

  initialized = true
  window.dataLayer = window.dataLayer || []
  window.gtag = function gtag(...args: unknown[]) {
    window.dataLayer?.push(args)
  }

  window.gtag('js', new Date())
  window.gtag('config', measurementId, { send_page_view: false })
  loadGoogleAnalyticsScript(measurementId)

  router.afterEach((to) => {
    trackPageView(to.fullPath, document.title)
  })

  void router.isReady().then(() => {
    trackPageView(router.currentRoute.value.fullPath, document.title)
  })
}
