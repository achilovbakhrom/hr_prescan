import type { Application, ApplicationStatus } from '@/shared/types/candidate.types'

export function getTableOverallScore(c: Application): number | null {
  const cv = c.matchScore != null ? Number(c.matchScore) : null
  const ps = c.prescanningScore != null ? Number(c.prescanningScore) * 10 : null
  const iv = c.interviewScore != null ? Number(c.interviewScore) * 10 : null
  if (cv != null && ps != null && iv != null) return Math.round(cv * 0.2 + ps * 0.3 + iv * 0.5)
  if (cv != null && ps != null) return Math.round(cv * 0.4 + ps * 0.6)
  if (ps != null && iv != null) return Math.round(ps * 0.4 + iv * 0.6)
  if (cv != null) return Math.round(cv)
  if (ps != null) return Math.round(ps)
  if (iv != null) return Math.round(iv)
  return null
}

export function getTableScoreClasses(score: number): string {
  if (score >= 70) return 'border-emerald-400 text-emerald-600'
  if (score >= 45) return 'border-amber-400 text-amber-600'
  return 'border-red-400 text-red-500'
}

export function getTableScoreBadge(score: number, max: number): string {
  const pct = (score / max) * 100
  if (pct >= 70) return 'bg-emerald-50 text-emerald-700'
  if (pct >= 45) return 'bg-amber-50 text-amber-700'
  return 'bg-red-50 text-red-700'
}

interface MenuItem {
  label: string
  icon: string
  command: () => void
  separator?: boolean
}

export function buildRowMenuItems(
  c: Application,
  interviewEnabled: boolean,
  viewDetail: (c: Application) => void,
  confirmStatus: (c: Application, toStatus: ApplicationStatus) => void,
  t: (key: string) => string,
): MenuItem[] {
  const s = c.status
  const items: MenuItem[] = []

  items.push({ label: t('common.viewDetails'), icon: 'pi pi-eye', command: () => viewDetail(c) })
  items.push({ label: '', icon: '', command: () => {}, separator: true })

  if (s === 'applied') {
    items.push({ label: t('candidates.actions.moveToPrescanned'), icon: 'pi pi-arrow-right', command: () => confirmStatus(c, 'prescanned') })
  }
  if (s === 'prescanned' && interviewEnabled) {
    items.push({ label: t('candidates.actions.moveToInterviewed'), icon: 'pi pi-arrow-right', command: () => confirmStatus(c, 'interviewed') })
  }
  if (s !== 'shortlisted' && s !== 'hired' && s !== 'archived') {
    items.push({ label: t('candidates.actions.shortlist'), icon: 'pi pi-star', command: () => confirmStatus(c, 'shortlisted') })
  }
  if (s !== 'hired' && s !== 'archived') {
    items.push({ label: t('candidates.actions.hire'), icon: 'pi pi-check-circle', command: () => confirmStatus(c, 'hired') })
  }
  if (s !== 'rejected' && s !== 'hired' && s !== 'archived') {
    items.push({ label: '', icon: '', command: () => {}, separator: true })
    items.push({ label: t('candidates.actions.reject'), icon: 'pi pi-times', command: () => confirmStatus(c, 'rejected') })
  }
  if (s === 'rejected' || s === 'expired' || s === 'shortlisted' || s === 'hired') {
    items.push({ label: t('candidates.actions.archive'), icon: 'pi pi-inbox', command: () => confirmStatus(c, 'archived') })
  }
  if (s !== 'applied' && s !== 'archived') {
    items.push({ label: t('candidates.actions.reset'), icon: 'pi pi-refresh', command: () => confirmStatus(c, 'applied') })
  }
  if (s === 'archived') {
    items.push({ label: t('candidates.actions.restore'), icon: 'pi pi-refresh', command: () => confirmStatus(c, 'applied') })
  }

  return items
}
