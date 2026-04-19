/**
 * ChartTheme — resolves theme tokens into chart.js color values.
 * Reads from CSS custom properties so the chart always matches the theme.
 */

function readVar(name: string, fallback = '#64748b'): string {
  if (typeof window === 'undefined') return fallback
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  return v || fallback
}

export function chartColors() {
  return {
    accent: readVar('--color-accent', '#2563eb'),
    accentAi: readVar('--color-accent-ai', '#7c5cff'),
    accentCelebrate: readVar('--color-accent-celebrate', '#ff9b73'),
    success: readVar('--color-success', '#10b981'),
    warning: readVar('--color-warning', '#f59e0b'),
    danger: readVar('--color-danger', '#ef4444'),
    info: readVar('--color-info', '#0ea5e9'),
    textSecondary: readVar('--color-text-secondary', '#374151'),
    textMuted: readVar('--color-text-muted', '#6b7280'),
    borderSoft: readVar('--color-border-soft', '#e5e7eb'),
  }
}

export function gridLineColor(): string {
  return chartColors().borderSoft
}

export function tierColor(tier: string): string {
  const c = chartColors()
  const map: Record<string, string> = {
    free: c.textMuted,
    starter: c.accent,
    professional: c.accentAi,
    enterprise: c.warning,
  }
  return map[tier] || c.textMuted
}

export function monthLabel(m: string): string {
  const [y, mo] = m.split('-')
  return new Date(parseInt(y), parseInt(mo) - 1, 1).toLocaleDateString(undefined, {
    month: 'short',
    year: '2-digit',
  })
}
