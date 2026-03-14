export type NotificationType =
  | 'application_received'
  | 'interview_scheduled'
  | 'interview_completed'
  | 'interview_reminder'
  | 'status_changed'
  | 'invitation_received'
  | 'system'

export interface Notification {
  id: string
  type: NotificationType
  title: string
  message: string
  data: Record<string, string>
  isRead: boolean
  createdAt: string
}
