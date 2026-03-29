import { useConfirm } from 'primevue/useconfirm'
import { useCandidateStore } from '@/features/candidates/stores/candidate.store'
import { candidateService } from '@/features/candidates/services/candidate.service'
import type { Application, ApplicationStatus } from '@/shared/types/candidate.types'

export function useCandidateActions(
  vacancyId: () => string,
  fetchCandidates: () => void,
) {
  const confirm = useConfirm()
  const candidateStore = useCandidateStore()

  function confirmRowStatus(c: Application, toStatus: ApplicationStatus): void {
    const label = toStatus.replace(/_/g, ' ')
    confirm.require({
      message: `Move ${c.candidateName} to "${label}"?`,
      header: 'Change Status',
      icon: toStatus === 'rejected' ? 'pi pi-exclamation-triangle' : 'pi pi-question-circle',
      acceptClass: toStatus === 'rejected' ? 'p-button-danger' : '',
      acceptLabel: 'Yes',
      rejectLabel: 'Cancel',
      accept: async () => {
        await candidateStore.updateStatus(c.id, toStatus).catch(() => {})
      },
    })
  }

  function handleKanbanStatusChange(candidateId: string, status: ApplicationStatus): void {
    const candidate = candidateStore.candidates.find((c) => c.id === candidateId)
    if (!candidate) return

    const statusLabel = status.replace(/_/g, ' ')
    const isReset = status === 'applied'
    const message = isReset
      ? `Reset ${candidate.candidateName} back to "Applied"?`
      : `Move ${candidate.candidateName} to "${statusLabel}"?`

    confirm.require({
      message,
      header: isReset ? 'Reset Candidate Status' : 'Confirm Status Change',
      icon: isReset ? 'pi pi-refresh' : 'pi pi-exclamation-triangle',
      acceptLabel: isReset ? 'Yes, reset' : 'Yes, move',
      rejectLabel: 'Cancel',
      accept: async () => {
        await candidateStore.updateStatus(candidateId, status).catch(() => {})
      },
    })
  }

  function handleBatchMove(fromStatus: ApplicationStatus, toStatus: ApplicationStatus): void {
    const count = candidateStore.candidates.filter((c) => c.status === fromStatus).length
    if (!count) return

    confirm.require({
      message: `Move all ${count} "${fromStatus}" candidate(s) to "${toStatus}"?`,
      header: 'Batch Move',
      icon: 'pi pi-arrows-alt',
      acceptLabel: 'Yes, move all',
      rejectLabel: 'Cancel',
      accept: async () => {
        await candidateService.batchMove(vacancyId(), { fromStatus, toStatus })
        fetchCandidates()
      },
    })
  }

  function handleBatchMoveByScore(
    fromStatus: ApplicationStatus,
    toStatus: ApplicationStatus,
    scoreField: string,
    threshold: number,
    direction: 'below' | 'above',
  ): void {
    const dirLabel = direction === 'below' ? '<' : '>'
    const fieldLabel =
      scoreField === 'match_score'
        ? 'CV match'
        : scoreField === 'prescanning_score'
          ? 'prescan score'
          : 'interview score'

    confirm.require({
      message: `Move "${fromStatus}" candidates with ${fieldLabel} ${dirLabel} ${threshold} to "${toStatus}"?`,
      header: 'Batch Move by Score',
      icon: 'pi pi-filter',
      acceptLabel: 'Yes, move',
      rejectLabel: 'Cancel',
      accept: async () => {
        await candidateService.batchMove(vacancyId(), {
          fromStatus,
          toStatus,
          scoreField: scoreField as 'match_score' | 'prescanning_score' | 'interview_score',
          ...(direction === 'below' ? { maxScore: threshold } : { minScore: threshold }),
        })
        fetchCandidates()
      },
    })
  }

  function handleBatchMoveNoCv(fromStatus: ApplicationStatus, toStatus: ApplicationStatus): void {
    confirm.require({
      message: `Move all "${fromStatus}" candidates without CV to "${toStatus}"?`,
      header: 'Batch Move (No CV)',
      icon: 'pi pi-file',
      acceptLabel: 'Yes, move',
      rejectLabel: 'Cancel',
      accept: async () => {
        await candidateService.batchMove(vacancyId(), { fromStatus, toStatus, hasCv: false })
        fetchCandidates()
      },
    })
  }

  function handleBatchMoveByDays(
    fromStatus: ApplicationStatus,
    toStatus: ApplicationStatus,
    days: number,
  ): void {
    confirm.require({
      message: `Move "${fromStatus}" candidates idle for more than ${days} days to "${toStatus}"?`,
      header: 'Batch Move (Idle)',
      icon: 'pi pi-clock',
      acceptLabel: 'Yes, move',
      rejectLabel: 'Cancel',
      accept: async () => {
        await candidateService.batchMove(vacancyId(), {
          fromStatus,
          toStatus,
          daysSinceApplied: days,
        })
        fetchCandidates()
      },
    })
  }

  function handleSoftDeleteAll(status: ApplicationStatus): void {
    const candidates = candidateStore.candidates.filter((c) => c.status === status)
    if (!candidates.length) return

    confirm.require({
      message: `Permanently hide all ${candidates.length} archived candidate(s)? They will no longer appear anywhere.`,
      header: 'Clear Archive',
      icon: 'pi pi-trash',
      acceptClass: 'p-button-danger',
      acceptLabel: 'Yes, clear all',
      rejectLabel: 'Cancel',
      accept: async () => {
        const ids = candidates.map((c) => c.id)
        await candidateService.softDelete(ids)
        fetchCandidates()
      },
    })
  }

  function handleBulkAction(
    selectedCandidates: Application[],
    status: ApplicationStatus,
    onClear: () => void,
  ): void {
    const count = selectedCandidates.length
    const label = status === 'shortlisted' ? 'shortlist' : 'reject'

    confirm.require({
      message: `Are you sure you want to ${label} ${count} candidate(s)?`,
      header: 'Confirm Bulk Action',
      icon: 'pi pi-exclamation-triangle',
      acceptClass: status === 'rejected' ? 'p-button-danger' : 'p-button-success',
      accept: async () => {
        const ids = selectedCandidates.map((c) => c.id)
        await candidateStore.bulkUpdateStatus(ids, status).catch(() => {})
        onClear()
      },
    })
  }

  return {
    confirmRowStatus,
    handleKanbanStatusChange,
    handleBatchMove,
    handleBatchMoveByScore,
    handleBatchMoveNoCv,
    handleBatchMoveByDays,
    handleSoftDeleteAll,
    handleBulkAction,
  }
}
