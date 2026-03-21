<script setup lang="ts">
import { computed } from 'vue'
import { ref } from 'vue'
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
  openMessages: []
}>()

const confirm = useConfirm()
const showEmailDialog = ref(false)

const statusOptions = computed(() => {
  const options: { label: string; value: ApplicationStatus }[] = []
  const s = props.currentStatus

  if (s !== 'shortlisted') {
    options.push({ label: 'Shortlist', value: 'shortlisted' })
  }
  if (s !== 'rejected') {
    options.push({ label: 'Reject', value: 'rejected' })
  }
  if (s !== 'applied' && s !== 'interview_in_progress') {
    options.push({ label: 'Reset to Applied', value: 'applied' })
  }

  return options
})

const statusMessages: Record<string, { message: string; icon: string; acceptClass: string; acceptLabel: string }> = {
  shortlisted: {
    message: 'This will move them to the next stage.',
    icon: 'pi pi-check-circle',
    acceptClass: 'p-button-success',
    acceptLabel: 'Yes, shortlist',
  },
  rejected: {
    message: 'This will notify the candidate.',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    acceptLabel: 'Yes, reject',
  },
  applied: {
    message: 'This will reset them back to the initial state.',
    icon: 'pi pi-refresh',
    acceptClass: '',
    acceptLabel: 'Yes, reset',
  },
}

function handleStatusChange(event: { value: ApplicationStatus }): void {
  const status = event.value
  const config = statusMessages[status] ?? {
    message: `Change status to "${status.replace(/_/g, ' ')}"?`,
    icon: 'pi pi-question-circle',
    acceptClass: '',
    acceptLabel: 'Confirm',
  }

  confirm.require({
    message: `${props.candidateName}: ${config.message}`,
    header: status === 'applied' ? 'Reset Candidate Status' : `Confirm ${status.replace(/_/g, ' ')}`,
    icon: config.icon,
    acceptClass: config.acceptClass,
    acceptLabel: config.acceptLabel,
    rejectLabel: 'Cancel',
    accept: () => emit('statusChange', status),
  })
}

</script>

<template>
  <div class="flex flex-wrap items-center gap-2">
    <Button
      label="Send Email"
      icon="pi pi-envelope"
      size="small"
      severity="secondary"
      outlined
      @click="showEmailDialog = true"
    />
    <Button
      label="Messages"
      icon="pi pi-comments"
      size="small"
      severity="secondary"
      outlined
      @click="emit('openMessages')"
    />
    <Dropdown
      :model-value="null"
      :options="statusOptions"
      option-label="label"
      option-value="value"
      placeholder="Change status"
      class="w-44"
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
