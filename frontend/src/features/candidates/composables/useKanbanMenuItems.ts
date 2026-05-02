import type { ApplicationStatus } from '../types/candidate.types'

type MenuItem = { label: string; icon: string; command: () => void; separator?: boolean }
type Translate = (key: string) => string

interface KanbanMenuDeps {
  t: Translate
  columnCounts: Record<string, number>
  interviewEnabled: boolean
  emitBatchMove: (from: ApplicationStatus, to: ApplicationStatus) => void
  emitBatchMoveNoCv: (from: ApplicationStatus, to: ApplicationStatus) => void
  emitSoftDeleteAll: (status: ApplicationStatus) => void
  openThresholdDialog: (
    from: ApplicationStatus,
    to: ApplicationStatus,
    field: string,
    dir: 'below' | 'above',
  ) => void
  openDaysDialog: (from: ApplicationStatus, to: ApplicationStatus) => void
}

export function buildColumnMenuItems(status: ApplicationStatus, deps: KanbanMenuDeps): MenuItem[] {
  const {
    t,
    columnCounts,
    interviewEnabled,
    emitBatchMove,
    emitBatchMoveNoCv,
    emitSoftDeleteAll,
    openThresholdDialog,
    openDaysDialog,
  } = deps
  const items: MenuItem[] = []
  if (columnCounts[status] === 0)
    return [{ label: t('candidates.noCandidates'), icon: 'pi pi-info-circle', command: () => {} }]

  const bm = emitBatchMove
  const sep: MenuItem = { label: '', icon: '', command: () => {}, separator: true }

  if (status === 'applied') {
    items.push({
      label: t('candidates.kanbanActions.rejectAll'),
      icon: 'pi pi-times',
      command: () => bm('applied', 'rejected'),
    })
    items.push({
      label: t('candidates.kanbanActions.rejectByCvMatch'),
      icon: 'pi pi-filter',
      command: () => openThresholdDialog('applied', 'rejected', 'match_score', 'below'),
    })
    items.push({
      label: t('candidates.kanbanActions.rejectNoCv'),
      icon: 'pi pi-file',
      command: () => emitBatchMoveNoCv('applied', 'rejected'),
    })
    items.push({
      label: t('candidates.kanbanActions.rejectIdle'),
      icon: 'pi pi-clock',
      command: () => openDaysDialog('applied', 'rejected'),
    })
    items.push(sep, {
      label: t('candidates.kanbanActions.shortlistAll'),
      icon: 'pi pi-star',
      command: () => bm('applied', 'shortlisted'),
    })
    items.push({
      label: t('candidates.kanbanActions.hireAll'),
      icon: 'pi pi-check-circle',
      command: () => bm('applied', 'hired'),
    })
    items.push({
      label: t('candidates.kanbanActions.archiveAll'),
      icon: 'pi pi-inbox',
      command: () => bm('applied', 'archived'),
    })
  } else if (status === 'prescanned') {
    if (interviewEnabled)
      items.push({
        label: t('candidates.kanbanActions.moveAllToInterviewed'),
        icon: 'pi pi-arrow-right',
        command: () => bm('prescanned', 'interviewed'),
      })
    items.push({
      label: t('candidates.kanbanActions.shortlistAll'),
      icon: 'pi pi-star',
      command: () => bm('prescanned', 'shortlisted'),
    })
    items.push({
      label: t('candidates.kanbanActions.hireAll'),
      icon: 'pi pi-check-circle',
      command: () => bm('prescanned', 'hired'),
    })
    items.push(sep, {
      label: t('candidates.kanbanActions.rejectAll'),
      icon: 'pi pi-times',
      command: () => bm('prescanned', 'rejected'),
    })
    items.push({
      label: t('candidates.kanbanActions.rejectByPrescanScore'),
      icon: 'pi pi-filter',
      command: () => openThresholdDialog('prescanned', 'rejected', 'prescanning_score', 'below'),
    })
    items.push({
      label: t('candidates.kanbanActions.shortlistByPrescanScore'),
      icon: 'pi pi-filter',
      command: () => openThresholdDialog('prescanned', 'shortlisted', 'prescanning_score', 'above'),
    })
    items.push({
      label: t('candidates.kanbanActions.archiveAll'),
      icon: 'pi pi-inbox',
      command: () => bm('prescanned', 'archived'),
    })
  } else if (status === 'interviewed') {
    items.push({
      label: t('candidates.kanbanActions.shortlistAll'),
      icon: 'pi pi-star',
      command: () => bm('interviewed', 'shortlisted'),
    })
    items.push({
      label: t('candidates.kanbanActions.hireAll'),
      icon: 'pi pi-check-circle',
      command: () => bm('interviewed', 'hired'),
    })
    items.push(sep, {
      label: t('candidates.kanbanActions.rejectAll'),
      icon: 'pi pi-times',
      command: () => bm('interviewed', 'rejected'),
    })
    items.push({
      label: t('candidates.kanbanActions.rejectByInterviewScore'),
      icon: 'pi pi-filter',
      command: () => openThresholdDialog('interviewed', 'rejected', 'interview_score', 'below'),
    })
    items.push({
      label: t('candidates.kanbanActions.shortlistByInterviewScore'),
      icon: 'pi pi-filter',
      command: () => openThresholdDialog('interviewed', 'shortlisted', 'interview_score', 'above'),
    })
    items.push({
      label: t('candidates.kanbanActions.archiveAll'),
      icon: 'pi pi-inbox',
      command: () => bm('interviewed', 'archived'),
    })
  } else if (status === 'shortlisted') {
    items.push({
      label: t('candidates.kanbanActions.hireAll'),
      icon: 'pi pi-check-circle',
      command: () => bm('shortlisted', 'hired'),
    })
    items.push({
      label: t('candidates.kanbanActions.rejectAll'),
      icon: 'pi pi-times',
      command: () => bm('shortlisted', 'rejected'),
    })
    items.push({
      label: t('candidates.kanbanActions.archiveAll'),
      icon: 'pi pi-inbox',
      command: () => bm('shortlisted', 'archived'),
    })
  } else if (status === 'hired') {
    items.push({
      label: t('candidates.kanbanActions.archiveAll'),
      icon: 'pi pi-inbox',
      command: () => bm('hired', 'archived'),
    })
  } else if (status === 'rejected') {
    items.push({
      label: t('candidates.kanbanActions.archiveAll'),
      icon: 'pi pi-inbox',
      command: () => bm('rejected', 'archived'),
    })
    items.push({
      label: t('candidates.kanbanActions.resetAllToApplied'),
      icon: 'pi pi-refresh',
      command: () => bm('rejected', 'applied'),
    })
  } else if (status === 'archived') {
    items.push({
      label: t('candidates.kanbanActions.restoreAllToApplied'),
      icon: 'pi pi-refresh',
      command: () => bm('archived', 'applied'),
    })
    items.push({
      label: t('candidates.kanbanActions.clearAll'),
      icon: 'pi pi-trash',
      command: () => emitSoftDeleteAll('archived'),
    })
  }
  return items
}
