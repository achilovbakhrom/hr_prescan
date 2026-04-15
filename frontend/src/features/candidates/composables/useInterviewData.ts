import { ref } from 'vue'
import { candidateService } from '../services/candidate.service'

export function useInterviewData() {
  const prescanningScore = ref<number | null>(null)
  const interviewScore = ref<number | null>(null)
  const aiSummary = ref<string | null>(null)
  const aiSummaryTranslations = ref<Record<string, string>>({})
  const aiSummaryInterviewId = ref<string | null>(null)

  async function fetchInterviewData(candidateId: string, hasInterview: boolean): Promise<void> {
    // Fetch prescanning interview data
    try {
      const data = (await candidateService.getCandidateInterview(candidateId, 'prescanning')) as Record<string, unknown>
      prescanningScore.value = (data.overallScore as number) ?? null
      aiSummary.value = (data.aiSummary as string) ?? null
      aiSummaryTranslations.value = (data.aiSummaryTranslations as Record<string, string>) ?? {}
      aiSummaryInterviewId.value = (data.id as string) ?? null
    } catch {
      // no prescanning interview yet
    }

    // Fetch interview data if interview is enabled
    if (hasInterview) {
      try {
        const data = (await candidateService.getCandidateInterview(candidateId, 'interview')) as Record<string, unknown>
        interviewScore.value = (data.overallScore as number) ?? null
        if (!aiSummary.value) {
          aiSummary.value = (data.aiSummary as string) ?? null
          aiSummaryTranslations.value = (data.aiSummaryTranslations as Record<string, string>) ?? {}
          aiSummaryInterviewId.value = (data.id as string) ?? null
        }
      } catch {
        // no interview yet
      }
    }
  }

  return {
    prescanningScore,
    interviewScore,
    aiSummary,
    aiSummaryTranslations,
    aiSummaryInterviewId,
    fetchInterviewData,
  }
}
