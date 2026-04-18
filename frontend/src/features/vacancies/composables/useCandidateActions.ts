import { useConfirm } from 'primevue/useconfirm'
import { useI18n } from 'vue-i18n'
import { useCandidateStore } from '@/features/candidates/stores/candidate.store'
import { candidateService } from '@/features/candidates/services/candidate.service'
import type { Application, ApplicationStatus } from '@/shared/types/candidate.types'

const STATUS_DIALOG_KEY: Record<
  ApplicationStatus,
  { message: string; accept: string; icon: string; acceptClass: string } | undefined
> = {
  prescanned: {
    message: 'candidates.dialogs.msgPrescanned',
    accept: 'candidates.dialogs.yesMove',
    icon: 'pi pi-check',
    acceptClass: 'p-button-info',
  },
  interviewed: {
    message: 'candidates.dialogs.msgInterviewed',
    accept: 'candidates.dialogs.yesMove',
    icon: 'pi pi-check',
    acceptClass: 'p-button-info',
  },
  shortlisted: {
    message: 'candidates.dialogs.msgShortlisted',
    accept: 'candidates.dialogs.yesShortlist',
    icon: 'pi pi-check-circle',
    acceptClass: 'p-button-success',
  },
  hired: {
    message: 'candidates.dialogs.msgHired',
    accept: 'candidates.dialogs.yesHire',
    icon: 'pi pi-check-circle',
    acceptClass: 'p-button-success',
  },
  rejected: {
    message: 'candidates.dialogs.msgRejected',
    accept: 'candidates.dialogs.yesReject',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
  },
  archived: {
    message: 'candidates.dialogs.msgArchived',
    accept: 'candidates.dialogs.yesMove',
    icon: 'pi pi-inbox',
    acceptClass: '',
  },
  applied: {
    message: 'candidates.dialogs.msgApplied',
    accept: 'candidates.dialogs.yesReset',
    icon: 'pi pi-refresh',
    acceptClass: '',
  },
  expired: undefined,
}

export function useCandidateActions(vacancyId: () => string, fetchCandidates: () => void) {
  const confirm = useConfirm()
  const candidateStore = useCandidateStore()
  const { t } = useI18n()

  function confirmStatusDialog(
    c: Application,
    toStatus: ApplicationStatus,
    onConfirm: () => Promise<void>,
  ): void {
    const cfg = STATUS_DIALOG_KEY[toStatus]
    if (!cfg) return
    confirm.require({
      message: t(cfg.message, { name: c.candidateName }),
      header:
        toStatus === 'applied'
          ? t('candidates.dialogs.resetHeader')
          : t('candidates.dialogs.statusChangeHeader'),
      icon: cfg.icon,
      acceptClass: cfg.acceptClass,
      acceptLabel: t(cfg.accept),
      rejectLabel: t('common.cancel'),
      accept: () => {
        onConfirm()
      },
    })
  }

  function confirmRowStatus(c: Application, toStatus: ApplicationStatus): void {
    confirmStatusDialog(c, toStatus, async () => {
      await candidateStore.updateStatus(c.id, toStatus).catch(() => {})
    })
  }

  function handleKanbanStatusChange(candidateId: string, status: ApplicationStatus): void {
    const candidate = candidateStore.candidates.find((c) => c.id === candidateId)
    if (!candidate) return
    confirmStatusDialog(candidate, status, async () => {
      await candidateStore.updateStatus(candidateId, status).catch(() => {})
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
