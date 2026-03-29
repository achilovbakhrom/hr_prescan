import type { ApplicationStatus } from '../types/candidate.types'

type MenuItem = { label: string; icon: string; command: () => void; separator?: boolean }

interface KanbanMenuDeps {
  columnCounts: Record<string, number>
  interviewEnabled: boolean
  emitBatchMove: (from: ApplicationStatus, to: ApplicationStatus) => void
  emitBatchMoveNoCv: (from: ApplicationStatus, to: ApplicationStatus) => void
  emitSoftDeleteAll: (status: ApplicationStatus) => void
  openThresholdDialog: (from: ApplicationStatus, to: ApplicationStatus, field: string, dir: 'below' | 'above') => void
  openDaysDialog: (from: ApplicationStatus, to: ApplicationStatus) => void
}

export function buildColumnMenuItems(status: ApplicationStatus, deps: KanbanMenuDeps): MenuItem[] {
  const { columnCounts, interviewEnabled, emitBatchMove, emitBatchMoveNoCv, emitSoftDeleteAll, openThresholdDialog, openDaysDialog } = deps
  const items: MenuItem[] = []
  if (columnCounts[status] === 0) return [{ label: 'No candidates', icon: 'pi pi-info-circle', command: () => {} }]

  const bm = emitBatchMove
  const sep: MenuItem = { label: '', icon: '', command: () => {}, separator: true }

  if (status === 'applied') {
    items.push({ label: 'Reject all', icon: 'pi pi-times', command: () => bm('applied', 'rejected') })
    items.push({ label: 'Reject by CV match < ...', icon: 'pi pi-filter', command: () => openThresholdDialog('applied', 'rejected', 'match_score', 'below') })
    items.push({ label: 'Reject with no CV', icon: 'pi pi-file', command: () => emitBatchMoveNoCv('applied', 'rejected') })
    items.push({ label: 'Reject idle > ... days', icon: 'pi pi-clock', command: () => openDaysDialog('applied', 'rejected') })
    items.push(sep, { label: 'Shortlist all', icon: 'pi pi-star', command: () => bm('applied', 'shortlisted') })
    items.push({ label: 'Hire all', icon: 'pi pi-check-circle', command: () => bm('applied', 'hired') })
    items.push({ label: 'Archive all', icon: 'pi pi-inbox', command: () => bm('applied', 'archived') })
  } else if (status === 'prescanned') {
    if (interviewEnabled) items.push({ label: 'Move all to Interviewed', icon: 'pi pi-arrow-right', command: () => bm('prescanned', 'interviewed') })
    items.push({ label: 'Shortlist all', icon: 'pi pi-star', command: () => bm('prescanned', 'shortlisted') })
    items.push({ label: 'Hire all', icon: 'pi pi-check-circle', command: () => bm('prescanned', 'hired') })
    items.push(sep, { label: 'Reject all', icon: 'pi pi-times', command: () => bm('prescanned', 'rejected') })
    items.push({ label: 'Reject by prescan score < ...', icon: 'pi pi-filter', command: () => openThresholdDialog('prescanned', 'rejected', 'prescanning_score', 'below') })
    items.push({ label: 'Shortlist by prescan score > ...', icon: 'pi pi-filter', command: () => openThresholdDialog('prescanned', 'shortlisted', 'prescanning_score', 'above') })
    items.push({ label: 'Archive all', icon: 'pi pi-inbox', command: () => bm('prescanned', 'archived') })
  } else if (status === 'interviewed') {
    items.push({ label: 'Shortlist all', icon: 'pi pi-star', command: () => bm('interviewed', 'shortlisted') })
    items.push({ label: 'Hire all', icon: 'pi pi-check-circle', command: () => bm('interviewed', 'hired') })
    items.push(sep, { label: 'Reject all', icon: 'pi pi-times', command: () => bm('interviewed', 'rejected') })
    items.push({ label: 'Reject by interview score < ...', icon: 'pi pi-filter', command: () => openThresholdDialog('interviewed', 'rejected', 'interview_score', 'below') })
    items.push({ label: 'Shortlist by interview score > ...', icon: 'pi pi-filter', command: () => openThresholdDialog('interviewed', 'shortlisted', 'interview_score', 'above') })
    items.push({ label: 'Archive all', icon: 'pi pi-inbox', command: () => bm('interviewed', 'archived') })
  } else if (status === 'shortlisted') {
    items.push({ label: 'Hire all', icon: 'pi pi-check-circle', command: () => bm('shortlisted', 'hired') })
    items.push({ label: 'Reject all', icon: 'pi pi-times', command: () => bm('shortlisted', 'rejected') })
    items.push({ label: 'Archive all', icon: 'pi pi-inbox', command: () => bm('shortlisted', 'archived') })
  } else if (status === 'hired') {
    items.push({ label: 'Archive all', icon: 'pi pi-inbox', command: () => bm('hired', 'archived') })
  } else if (status === 'rejected') {
    items.push({ label: 'Archive all', icon: 'pi pi-inbox', command: () => bm('rejected', 'archived') })
    items.push({ label: 'Reset all to Applied', icon: 'pi pi-refresh', command: () => bm('rejected', 'applied') })
  } else if (status === 'archived') {
    items.push({ label: 'Restore all to Applied', icon: 'pi pi-refresh', command: () => bm('archived', 'applied') })
    items.push({ label: 'Clear all (soft delete)', icon: 'pi pi-trash', command: () => emitSoftDeleteAll('archived') })
  }
  return items
}
