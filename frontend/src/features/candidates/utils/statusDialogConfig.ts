import type { ApplicationStatus } from '../types/candidate.types'

export const STATUS_DIALOG_KEY: Record<
  ApplicationStatus,
  { message: string; accept: string; icon: string; acceptClass: string } | undefined
> = {
  prescanned: {
    message: 'candidates.dialogs.msgPrescanned',
    accept: 'candidates.dialogs.yesMove',
    icon: 'pi pi-check',
    acceptClass: 'p-button-info',
  },
  interviewed: {
    message: 'candidates.dialogs.msgInterviewed',
    accept: 'candidates.dialogs.yesMove',
    icon: 'pi pi-check',
    acceptClass: 'p-button-info',
  },
  shortlisted: {
    message: 'candidates.dialogs.msgShortlisted',
    accept: 'candidates.dialogs.yesShortlist',
    icon: 'pi pi-check-circle',
    acceptClass: 'p-button-success',
  },
  hired: {
    message: 'candidates.dialogs.msgHired',
    accept: 'candidates.dialogs.yesHire',
    icon: 'pi pi-check-circle',
    acceptClass: 'p-button-success',
  },
  rejected: {
    message: 'candidates.dialogs.msgRejected',
    accept: 'candidates.dialogs.yesReject',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
  },
  archived: {
    message: 'candidates.dialogs.msgArchived',
    accept: 'candidates.dialogs.yesMove',
    icon: 'pi pi-inbox',
    acceptClass: '',
  },
  applied: {
    message: 'candidates.dialogs.msgApplied',
    accept: 'candidates.dialogs.yesReset',
    icon: 'pi pi-refresh',
    acceptClass: '',
  },
  expired: undefined,
}
