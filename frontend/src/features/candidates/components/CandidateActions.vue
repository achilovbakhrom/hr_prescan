<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import ConfirmDialog from 'primevue/confirmdialog'
import { useConfirm } from 'primevue/useconfirm'
import type { ApplicationStatus } from '../types/candidate.types'
import SendEmailDialog from './SendEmailDialog.vue'

const props = defineProps<{
  candidateId: string
  candidateName: string
  candidateEmail: string
  vacancyId: string
  currentStatus: ApplicationStatus
  loading: boolean
}>()

const emit = defineEmits<{
  statusChange: [status: ApplicationStatus]
}>()

const { t } = useI18n()

const confirm = useConfirm()
const showEmailDialog = ref(false)

const statusOptions = computed(() => {
  const options: { label: string; value: ApplicationStatus }[] = []
  const s = props.currentStatus

  if (s === 'applied') {
    options.push({ label: t('candidates.actions.moveToPrescanned'), value: 'prescanned' })
  }
  if (s === 'prescanned') {
    options.push({ label: t('candidates.actions.moveToInterviewed'), value: 'interviewed' })
  }
  if (s !== 'shortlisted' && s !== 'hired' && s !== 'archived') {
    options.push({ label: t('candidates.actions.shortlist'), value: 'shortlisted' })
  }
  if (s !== 'hired' && s !== 'archived') {
    options.push({ label: t('candidates.actions.hire'), value: 'hired' })
  }
  if (s !== 'rejected' && s !== 'hired' && s !== 'archived') {
    options.push({ label: t('candidates.actions.reject'), value: 'rejected' })
  }
  if (s === 'rejected' || s === 'expired' || s === 'shortlisted' || s === 'hired') {
    options.push({ label: t('candidates.actions.archive'), value: 'archived' })
  }
  if (s !== 'applied' && s !== 'archived') {
    options.push({ label: t('candidates.actions.reset'), value: 'applied' })
  }
  if (s === 'archived') {
    options.push({ label: t('candidates.actions.restore'), value: 'applied' })
  }

  return options
})

const STATUS_CONFIG: Record<
  ApplicationStatus,
  { messageKey: string; icon: string; acceptClass: string; acceptKey: string } | undefined
> = {
  prescanned: {
    messageKey: 'candidates.dialogs.msgPrescanned',
    icon: 'pi pi-check',
    acceptClass: 'p-button-info',
    acceptKey: 'candidates.dialogs.yesMove',
  },
  interviewed: {
    messageKey: 'candidates.dialogs.msgInterviewed',
    icon: 'pi pi-check',
    acceptClass: 'p-button-info',
    acceptKey: 'candidates.dialogs.yesMove',
  },
  shortlisted: {
    messageKey: 'candidates.dialogs.msgShortlisted',
    icon: 'pi pi-check-circle',
    acceptClass: 'p-button-success',
    acceptKey: 'candidates.dialogs.yesShortlist',
  },
  hired: {
    messageKey: 'candidates.dialogs.msgHired',
    icon: 'pi pi-check-circle',
    acceptClass: 'p-button-success',
    acceptKey: 'candidates.dialogs.yesHire',
  },
  rejected: {
    messageKey: 'candidates.dialogs.msgRejected',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    acceptKey: 'candidates.dialogs.yesReject',
  },
  archived: {
    messageKey: 'candidates.dialogs.msgArchived',
    icon: 'pi pi-inbox',
    acceptClass: '',
    acceptKey: 'candidates.dialogs.yesArchive',
  },
  applied: {
    messageKey: 'candidates.dialogs.msgApplied',
    icon: 'pi pi-refresh',
    acceptClass: '',
    acceptKey: 'candidates.dialogs.yesReset',
  },
  expired: undefined,
}

function handleStatusChange(event: { value: ApplicationStatus }): void {
  const status = event.value
  const config = STATUS_CONFIG[status]
  if (!config) return

  confirm.require({
    message: t(config.messageKey, { name: props.candidateName }),
    header:
      status === 'applied'
        ? t('candidates.dialogs.resetHeader')
        : t('candidates.dialogs.statusChangeHeader'),
    icon: config.icon,
    acceptClass: config.acceptClass,
    acceptLabel: t(config.acceptKey),
    rejectLabel: t('common.cancel'),
    accept: () => emit('statusChange', status),
  })
}
</script>

<template>
  <div class="flex flex-wrap items-center gap-1.5 sm:gap-2">
    <Button
      :label="t('candidates.actions.sendEmail')"
      icon="pi pi-envelope"
      size="small"
      severity="secondary"
      outlined
      @click="showEmailDialog = true"
    />
    <Dropdown
      :model-value="null"
      :options="statusOptions"
      option-label="label"
      option-value="value"
      :placeholder="t('candidates.actions.changeStatus')"
      :disabled="props.loading"
      @change="handleStatusChange"
    />

    <ConfirmDialog />

    <SendEmailDialog
      :visible="showEmailDialog"
      :candidate-id="props.candidateId"
      :candidate-email="props.candidateEmail"
      @close="showEmailDialog = false"
    />
  </div>
</template>
