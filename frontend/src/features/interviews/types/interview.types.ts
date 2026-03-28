// Re-export shared types so intra-feature imports still work
export type { InterviewScore, IntegrityFlag, IntegrityFlagType, IntegritySeverity } from '@/shared/types/interview.types'

// Import shared types needed by feature-specific interfaces
import type { InterviewScore, IntegrityFlag } from '@/shared/types/interview.types'

export type InterviewStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled' | 'expired'

export type ScreeningMode = 'chat' | 'meet'

export type SessionType = 'prescanning' | 'interview'

export interface Interview {
  id: string
  applicationId: string
  candidateName: string
  vacancyTitle: string
  sessionType: SessionType
  screeningMode: ScreeningMode
  interviewToken: string
  startedAt: string | null
  durationMinutes: number
  status: InterviewStatus
  livekitRoomName: string
  overallScore: number | null
  language: string
  createdAt: string
}

export interface ChatMessage {
  role: 'ai' | 'candidate'
  text: string
  timestamp: string
  messageType?: 'text' | 'voice'
  audioUrl?: string
  duration?: number
}

export interface InterviewDetail extends Interview {
  candidateEmail: string
  candidateToken: string
  recordingPath: string
  transcript: TranscriptEntry[]
  chatHistory: ChatMessage[]
  aiSummary: string
  aiSummaryTranslations: Record<string, string>
  language: string
  scores: InterviewScore[]
  integrityFlags: IntegrityFlag[]
  updatedAt: string
}

export interface TranscriptEntry {
  speaker: string
  text: string
  timestamp: number
}
