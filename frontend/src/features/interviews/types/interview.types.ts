export type InterviewStatus = 'scheduled' | 'in_progress' | 'completed' | 'cancelled' | 'no_show'

export type IntegrityFlagType = 'face_not_visible' | 'multiple_faces' | 'gaze_deviation' | 'audio_anomaly' | 'cv_inconsistency'
export type IntegritySeverity = 'low' | 'medium' | 'high'

export interface Interview {
  id: string
  applicationId: string
  candidateName: string
  vacancyTitle: string
  scheduledAt: string
  durationMinutes: number
  status: InterviewStatus
  livekitRoomName: string
  overallScore: number | null
  createdAt: string
}

export interface InterviewDetail extends Interview {
  candidateToken: string
  recordingPath: string
  transcript: TranscriptEntry[]
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

export interface ScheduleInterviewRequest {
  scheduledAt: string
}
