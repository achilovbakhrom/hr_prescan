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

  // Forward moves
  if (s === 'applied') {
    options.push({ label: 'Move to Prescanned', value: 'prescanned' })
  }
  if (s === 'prescanned') {
    options.push({ label: 'Move to Interviewed', value: 'interviewed' })
  }
  if (s !== 'shortlisted' && s !== 'hired' && s !== 'archived') {
    options.push({ label: 'Shortlist', value: 'shortlisted' })
  }
  if (s !== 'hired' && s !== 'archived') {
    options.push({ label: 'Hire', value: 'hired' })
  }

  // Reject (from any active status)
  if (s !== 'rejected' && s !== 'hired' && s !== 'archived') {
    options.push({ label: 'Reject', value: 'rejected' })
  }

  // Archive
  if (s === 'rejected' || s === 'expired' || s === 'shortlisted' || s === 'hired') {
    options.push({ label: 'Archive', value: 'archived' })
  }

  // Reset (from any non-applied, non-archived)
  if (s !== 'applied' && s !== 'archived') {
    options.push({ label: 'Reset to Applied', value: 'applied' })
  }

  // Unarchive
  if (s === 'archived') {
    options.push({ label: 'Restore to Applied', value: 'applied' })
  }

  return options
})

const statusMessages: Record<string, { message: string; icon: string; acceptClass: string; acceptLabel: string }> = {
  prescanned: {
    message: 'This will mark the candidate as prescanned.',
    icon: 'pi pi-check',
    acceptClass: 'p-button-info',
    acceptLabel: 'Yes, move',
  },
  interviewed: {
    message: 'This will mark the candidate as interviewed.',
    icon: 'pi pi-check',
    acceptClass: 'p-button-info',
    acceptLabel: 'Yes, move',
  },
  shortlisted: {
    message: 'This will move them to the shortlist.',
    icon: 'pi pi-check-circle',
    acceptClass: 'p-button-success',
    acceptLabel: 'Yes, shortlist',
  },
  hired: {
    message: 'This will mark the candidate as hired.',
    icon: 'pi pi-check-circle',
    acceptClass: 'p-button-success',
    acceptLabel: 'Yes, hire',
  },
  rejected: {
    message: 'This will reject the candidate.',
    icon: 'pi pi-exclamation-triangle',
    acceptClass: 'p-button-danger',
    acceptLabel: 'Yes, reject',
  },
  archived: {
    message: 'This will archive the candidate. They can be restored later.',
    icon: 'pi pi-inbox',
    acceptClass: '',
    acceptLabel: 'Yes, archive',
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
  <div class="flex flex-wrap items-center gap-1.5 sm:gap-2">
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
