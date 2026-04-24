import { useConfirm } from 'primevue/useconfirm'
import { candidateService } from '../services/candidate.service'
import { useCandidateStore } from '../stores/candidate.store'
import type { Application, ApplicationStatus } from '../types/candidate.types'

type ScoreField = 'match_score' | 'prescanning_score' | 'interview_score'

function scoreValue(candidate: Application, field: string): number | null {
  if (field === 'match_score') return candidate.matchScore
  if (field === 'prescanning_score') return candidate.prescanningScore
  if (field === 'interview_score') return candidate.interviewScore
  return null
}

function olderThanDays(createdAt: string, days: number): boolean {
  const created = Date.parse(createdAt)
  if (Number.isNaN(created)) return false
  return created < Date.now() - days * 24 * 60 * 60 * 1000
}

export function useKanbanBatchActions(
  candidates: () => Application[],
  vacancyId: () => string,
  fetchCandidates: () => void,
) {
  const confirm = useConfirm()
  const candidateStore = useCandidateStore()

  async function moveIds(ids: string[], status: ApplicationStatus): Promise<void> {
    if (!ids.length) return
    await candidateStore.bulkUpdateStatus(ids, status)
  }

  function confirmMove(message: string, accept: () => Promise<void>): void {
    confirm.require({
      message,
      header: 'Batch Move',
      icon: 'pi pi-arrows-alt',
      acceptLabel: 'Yes, move',
      rejectLabel: 'Cancel',
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

    confirmMove(`Move all ${matching.length} "${fromStatus}" candidate(s) to "${toStatus}"?`, async () => {
      if (vacancyId()) await candidateService.batchMove(vacancyId(), { fromStatus, toStatus })
      else await moveIds(matching.map((candidate) => candidate.id), toStatus)
      fetchCandidates()
    })
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

    confirmMove(`Move ${matching.length} candidate(s) matching this score filter to "${toStatus}"?`, async () => {
      if (vacancyId()) {
        await candidateService.batchMove(vacancyId(), {
          fromStatus,
          toStatus,
          scoreField: scoreField as ScoreField,
          ...(direction === 'below' ? { maxScore: threshold } : { minScore: threshold }),
        })
      } else {
        await moveIds(matching.map((candidate) => candidate.id), toStatus)
      }
      fetchCandidates()
    })
  }

  function handleBatchMoveNoCv(fromStatus: ApplicationStatus, toStatus: ApplicationStatus): void {
    const matching = matchingStatus(fromStatus).filter((candidate) => !candidate.cvFile)
    if (!matching.length) return

    confirmMove(`Move ${matching.length} "${fromStatus}" candidate(s) without CV to "${toStatus}"?`, async () => {
      if (vacancyId()) await candidateService.batchMove(vacancyId(), { fromStatus, toStatus, hasCv: false })
      else await moveIds(matching.map((candidate) => candidate.id), toStatus)
      fetchCandidates()
    })
  }

  function handleBatchMoveByDays(
    fromStatus: ApplicationStatus,
    toStatus: ApplicationStatus,
    days: number,
  ): void {
    const matching = matchingStatus(fromStatus).filter((candidate) => olderThanDays(candidate.createdAt, days))
    if (!matching.length) return

    confirmMove(`Move ${matching.length} candidate(s) idle for more than ${days} days to "${toStatus}"?`, async () => {
      if (vacancyId()) await candidateService.batchMove(vacancyId(), { fromStatus, toStatus, daysSinceApplied: days })
      else await moveIds(matching.map((candidate) => candidate.id), toStatus)
      fetchCandidates()
    })
  }

  function handleSoftDeleteAll(status: ApplicationStatus): void {
    const matching = matchingStatus(status)
    if (!matching.length) return

    confirm.require({
      message: `Permanently hide all ${matching.length} archived candidate(s)?`,
      header: 'Clear Archive',
      icon: 'pi pi-trash',
      acceptClass: 'p-button-danger',
      acceptLabel: 'Yes, clear all',
      rejectLabel: 'Cancel',
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
