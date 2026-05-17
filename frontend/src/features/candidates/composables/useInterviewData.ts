import { ref } from 'vue'
import { candidateService } from '../services/candidate.service'
import type { DecisionSupport } from '@/shared/types/interview.types'

export interface CandidateAnalysisSession {
  id: string
  sessionType: 'prescanning' | 'interview'
  overallScore: number | null
  aiSummary: string
  aiSummaryTranslations: Record<string, string>
  decisionSupport?: DecisionSupport
}

export function useInterviewData() {
  const prescanningScore = ref<number | null>(null)
  const interviewScore = ref<number | null>(null)
  const aiSummary = ref<string | null>(null)
  const aiSummaryTranslations = ref<Record<string, string>>({})
  const aiSummaryInterviewId = ref<string | null>(null)
  const analysisSessions = ref<CandidateAnalysisSession[]>([])

  async function fetchInterviewData(candidateId: string, hasInterview: boolean): Promise<void> {
    analysisSessions.value = []
    try {
      const data = (await candidateService.getCandidateInterview(
        candidateId,
        'prescanning',
      )) as Record<string, unknown>
      prescanningScore.value = (data.overallScore as number) ?? null
      addAnalysisSession(data, 'prescanning')
      aiSummary.value = (data.aiSummary as string) || null
      aiSummaryTranslations.value = (data.aiSummaryTranslations as Record<string, string>) ?? {}
      aiSummaryInterviewId.value = (data.id as string) ?? null
    } catch {
      // no prescanning interview yet
    }

    if (hasInterview) {
      try {
        const data = (await candidateService.getCandidateInterview(
          candidateId,
          'interview',
        )) as Record<string, unknown>
        interviewScore.value = (data.overallScore as number) ?? null
        addAnalysisSession(data, 'interview')
        if (data.aiSummary) {
          aiSummary.value = (data.aiSummary as string) ?? null
          aiSummaryTranslations.value = (data.aiSummaryTranslations as Record<string, string>) ?? {}
          aiSummaryInterviewId.value = (data.id as string) ?? null
        }
      } catch {
        // no interview yet
      }
    }
  }

  function addAnalysisSession(
    data: Record<string, unknown>,
    sessionType: CandidateAnalysisSession['sessionType'],
  ): void {
    analysisSessions.value.push({
      id: String(data.id ?? ''),
      sessionType,
      overallScore: (data.overallScore as number) ?? null,
      aiSummary: String(data.aiSummary ?? ''),
      aiSummaryTranslations: (data.aiSummaryTranslations as Record<string, string>) ?? {},
      decisionSupport: data.decisionSupport as DecisionSupport | undefined,
    })
  }

  return {
    prescanningScore,
    interviewScore,
    aiSummary,
    aiSummaryTranslations,
    aiSummaryInterviewId,
    analysisSessions,
    fetchInterviewData,
  }
}
