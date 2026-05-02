import { useConfirm } from 'primevue/useconfirm'
import { useI18n } from 'vue-i18n'
import { candidateService } from '../services/candidate.service'
import { useCandidateStore } from '../stores/candidate.store'
import type { Application, ApplicationStatus } from '../types/candidate.types'
import {
  olderThanDays,
  scoreFieldLabel,
  scoreValue,
  statusLabel,
  type ScoreField,
} from '../utils/candidateActionLabels'

export function useKanbanBatchActions(
  candidates: () => Application[],
  vacancyId: () => string,
  fetchCandidates: () => void,
) {
  const confirm = useConfirm()
  const { t } = useI18n()
  const candidateStore = useCandidateStore()

  async function moveIds(ids: string[], status: ApplicationStatus): Promise<void> {
    if (!ids.length) return
    await candidateStore.bulkUpdateStatus(ids, status)
  }

  function confirmMove(message: string, accept: () => Promise<void>): void {
    confirm.require({
      message,
      header: t('candidates.dialogs.batchMoveHeader'),
      icon: 'pi pi-arrows-alt',
      acceptLabel: t('candidates.dialogs.yesMove'),
      rejectLabel: t('common.cancel'),
      accept: () => {
        void accept()
      },
    })
  }

  function matchingStatus(status: ApplicationStatus): Application[] {
    return candidates().filter((candidate) => candidate.status === status)
  }

  function handleBatchMove(fromStatus: ApplicationStatus, toStatus: ApplicationStatus): void {
    const matching = matchingStatus(fromStatus)
    if (!matching.length) return

    confirmMove(
      t('candidates.dialogs.batchMoveAllMessage', {
        count: matching.length,
        from: statusLabel(t, fromStatus),
        to: statusLabel(t, toStatus),
      }),
      async () => {
        if (vacancyId()) await candidateService.batchMove(vacancyId(), { fromStatus, toStatus })
        else
          await moveIds(
            matching.map((candidate) => candidate.id),
            toStatus,
          )
        fetchCandidates()
      },
    )
  }

  function handleBatchMoveByScore(
    fromStatus: ApplicationStatus,
    toStatus: ApplicationStatus,
    scoreField: string,
    threshold: number,
    direction: 'below' | 'above',
  ): void {
    const matching = matchingStatus(fromStatus).filter((candidate) => {
      const value = scoreValue(candidate, scoreField)
      if (value == null) return false
      return direction === 'below' ? value < threshold : value > threshold
    })
    if (!matching.length) return

    confirmMove(
      t('candidates.dialogs.batchMoveScoreMessage', {
        count: matching.length,
        field: scoreFieldLabel(t, scoreField),
        direction: t(`candidates.scoreDirections.${direction}`),
        threshold,
        to: statusLabel(t, toStatus),
      }),
      async () => {
        if (vacancyId()) {
          await candidateService.batchMove(vacancyId(), {
            fromStatus,
            toStatus,
            scoreField: scoreField as ScoreField,
            ...(direction === 'below' ? { maxScore: threshold } : { minScore: threshold }),
          })
        } else {
          await moveIds(
            matching.map((candidate) => candidate.id),
            toStatus,
          )
        }
        fetchCandidates()
      },
    )
  }

  function handleBatchMoveNoCv(fromStatus: ApplicationStatus, toStatus: ApplicationStatus): void {
    const matching = matchingStatus(fromStatus).filter((candidate) => !candidate.cvFile)
    if (!matching.length) return

    confirmMove(
      t('candidates.dialogs.batchMoveNoCvMessage', {
        count: matching.length,
        from: statusLabel(t, fromStatus),
        to: statusLabel(t, toStatus),
      }),
      async () => {
        if (vacancyId())
          await candidateService.batchMove(vacancyId(), { fromStatus, toStatus, hasCv: false })
        else
          await moveIds(
            matching.map((candidate) => candidate.id),
            toStatus,
          )
        fetchCandidates()
      },
    )
  }

  function handleBatchMoveByDays(
    fromStatus: ApplicationStatus,
    toStatus: ApplicationStatus,
    days: number,
  ): void {
    const matching = matchingStatus(fromStatus).filter((candidate) =>
      olderThanDays(candidate.createdAt, days),
    )
    if (!matching.length) return

    confirmMove(
      t('candidates.dialogs.batchMoveIdleMessage', {
        count: matching.length,
        days,
        to: statusLabel(t, toStatus),
      }),
      async () => {
        if (vacancyId())
          await candidateService.batchMove(vacancyId(), {
            fromStatus,
            toStatus,
            daysSinceApplied: days,
          })
        else
          await moveIds(
            matching.map((candidate) => candidate.id),
            toStatus,
          )
        fetchCandidates()
      },
    )
  }

  function handleSoftDeleteAll(status: ApplicationStatus): void {
    const matching = matchingStatus(status)
    if (!matching.length) return

    confirm.require({
      message: t('candidates.dialogs.clearArchiveMessage', { count: matching.length }),
      header: t('candidates.dialogs.clearArchiveHeader'),
      icon: 'pi pi-trash',
      acceptClass: 'p-button-danger',
      acceptLabel: t('candidates.dialogs.yesClearAll'),
      rejectLabel: t('common.cancel'),
      accept: async () => {
        await candidateService.softDelete(matching.map((candidate) => candidate.id))
        fetchCandidates()
      },
    })
  }

  return {
    handleBatchMove,
    handleBatchMoveByScore,
    handleBatchMoveNoCv,
    handleBatchMoveByDays,
    handleSoftDeleteAll,
  }
}
