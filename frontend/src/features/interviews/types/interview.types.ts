export type InterviewStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled' | 'expired'

export type ScreeningMode = 'chat' | 'meet'

export type IntegrityFlagType = 'face_not_visible' | 'multiple_faces' | 'gaze_deviation' | 'audio_anomaly' | 'cv_inconsistency'
export type IntegritySeverity = 'low' | 'medium' | 'high'

export interface Interview {
  id: string
  applicationId: string
  candidateName: string
  vacancyTitle: string
  screeningMode: ScreeningMode
  interviewToken: string
  startedAt: string | null
  durationMinutes: number
  status: InterviewStatus
  livekitRoomName: string
  overallScore: number | null
  createdAt: string
}

export interface ChatMessage {
  role: 'ai' | 'candidate'
  text: string
  timestamp: string
}

export interface InterviewDetail extends Interview {
  candidateToken: string
  recordingPath: string
  transcript: TranscriptEntry[]
  chatHistory: ChatMessage[]
  aiSummary: string
  scores: InterviewScore[]
  integrityFlags: IntegrityFlag[]
}

export interface InterviewScore {
  id: string
  criteriaId: string
  criteriaName: string
  score: number
  aiNotes: string
}

export interface IntegrityFlag {
  id: string
  flagType: IntegrityFlagType
  severity: IntegritySeverity
  description: string
  timestampSeconds: number | null
}

export interface TranscriptEntry {
  speaker: string
  text: string
  timestamp: number
}
