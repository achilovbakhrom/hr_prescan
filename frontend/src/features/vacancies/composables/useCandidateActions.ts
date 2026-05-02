import { useConfirm } from 'primevue/useconfirm'
import { useI18n } from 'vue-i18n'
import { useCandidateStore } from '@/features/candidates/stores/candidate.store'
import { candidateService } from '@/features/candidates/services/candidate.service'
import type { Application, ApplicationStatus } from '@/shared/types/candidate.types'
import { STATUS_DIALOG_KEY } from '@/features/candidates/utils/statusDialogConfig'
import {
  scoreFieldLabel,
  statusLabel,
  type ScoreField,
} from '@/features/candidates/utils/candidateActionLabels'
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
      message: t('candidates.dialogs.batchMoveAllMessage', {
        count,
        from: statusLabel(t, fromStatus),
        to: statusLabel(t, toStatus),
      }),
      header: t('candidates.dialogs.batchMoveHeader'),
      icon: 'pi pi-arrows-alt',
      acceptLabel: t('candidates.dialogs.yesMoveAll'),
      rejectLabel: t('common.cancel'),
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
    confirm.require({
      message: t('candidates.dialogs.batchMoveScoreFilterMessage', {
        from: statusLabel(t, fromStatus),
        field: scoreFieldLabel(t, scoreField),
        direction: t(`candidates.scoreDirections.${direction}`),
        threshold,
        to: statusLabel(t, toStatus),
      }),
      header: t('candidates.dialogs.batchMoveByScoreHeader'),
      icon: 'pi pi-filter',
      acceptLabel: t('candidates.dialogs.yesMove'),
      rejectLabel: t('common.cancel'),
      accept: async () => {
        await candidateService.batchMove(vacancyId(), {
          fromStatus,
          toStatus,
          scoreField: scoreField as ScoreField,
          ...(direction === 'below' ? { maxScore: threshold } : { minScore: threshold }),
        })
        fetchCandidates()
      },
    })
  }

  function handleBatchMoveNoCv(fromStatus: ApplicationStatus, toStatus: ApplicationStatus): void {
    confirm.require({
      message: t('candidates.dialogs.batchMoveNoCvAllMessage', {
        from: statusLabel(t, fromStatus),
        to: statusLabel(t, toStatus),
      }),
      header: t('candidates.dialogs.batchMoveNoCvHeader'),
      icon: 'pi pi-file',
      acceptLabel: t('candidates.dialogs.yesMove'),
      rejectLabel: t('common.cancel'),
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
      message: t('candidates.dialogs.batchMoveIdleFilterMessage', {
        from: statusLabel(t, fromStatus),
        days,
        to: statusLabel(t, toStatus),
      }),
      header: t('candidates.dialogs.batchMoveIdleHeader'),
      icon: 'pi pi-clock',
      acceptLabel: t('candidates.dialogs.yesMove'),
      rejectLabel: t('common.cancel'),
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
      message: t('candidates.dialogs.clearArchiveDetailedMessage', { count: candidates.length }),
      header: t('candidates.dialogs.clearArchiveHeader'),
      icon: 'pi pi-trash',
      acceptClass: 'p-button-danger',
      acceptLabel: t('candidates.dialogs.yesClearAll'),
      rejectLabel: t('common.cancel'),
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
    const label =
      status === 'shortlisted' ? t('candidates.actions.shortlist') : t('candidates.actions.reject')

    confirm.require({
      message: t('candidates.dialogs.bulkConfirmMessage', { action: label, count }),
      header: t('candidates.dialogs.bulkConfirmHeader'),
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
