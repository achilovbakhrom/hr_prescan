interface ExportMessage {
  role: 'ai' | 'candidate'
  text: string
  timestamp?: string | number | null
}

interface ExportScore {
  criteriaName: string
  score: number
  aiNotes?: string
}

interface ExportInterview {
  id: string
  overallScore: number | null
  aiSummary?: string
  scores: ExportScore[]
}

function formatTimestamp(value: string | number | null | undefined): string {
  if (typeof value === 'number') {
    const mins = Math.floor(value / 60)
    const secs = Math.floor(value % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }
  return value || ''
}

function buildTranscriptText(interview: ExportInterview, messages: ExportMessage[]): string {
  const lines = [
    `Interview ID: ${interview.id}`,
    `Overall score: ${interview.overallScore ?? 'N/A'}/10`,
    '',
    'AI summary',
    interview.aiSummary || 'N/A',
    '',
    'Scores',
    ...interview.scores.map(
      (score) =>
        `- ${score.criteriaName}: ${score.score}/10${score.aiNotes ? ` - ${score.aiNotes}` : ''}`,
    ),
    '',
    'Conversation',
    ...messages.map((message) => {
      const timestamp = formatTimestamp(message.timestamp)
      return `${timestamp ? `[${timestamp}] ` : ''}${message.role.toUpperCase()}: ${message.text}`
    }),
  ]
  return lines.join('\n')
}

function download(filename: string, content: string, type: string): void {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

export function exportTranscriptTxt(interview: ExportInterview, messages: ExportMessage[]): void {
  download(
    `interview-${interview.id}-transcript.txt`,
    buildTranscriptText(interview, messages),
    'text/plain;charset=utf-8',
  )
}

export function exportTranscriptDoc(interview: ExportInterview, messages: ExportMessage[]): void {
  const html = `<html><body><pre>${buildTranscriptText(interview, messages)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')}</pre></body></html>`
  download(`interview-${interview.id}-transcript.doc`, html, 'application/msword')
}
