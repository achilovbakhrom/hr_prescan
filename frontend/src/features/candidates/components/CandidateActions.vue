<script setup lang="ts">
import { ref } from 'vue'
import Button from 'primevue/button'
import Dropdown from 'primevue/dropdown'
import ConfirmDialog from 'primevue/confirmdialog'
import { useConfirm } from 'primevue/useconfirm'
import type { ApplicationStatus } from '../types/candidate.types'
import ScheduleHumanInterviewDialog from './ScheduleHumanInterviewDialog.vue'
import SendEmailDialog from './SendEmailDialog.vue'

const props = defineProps<{
  candidateId: string
  candidateName: string
  candidateEmail: string
  currentStatus: ApplicationStatus
  loading: boolean
}>()

const emit = defineEmits<{
  statusChange: [status: ApplicationStatus]
  openMessages: []
}>()

const confirm = useConfirm()
const showScheduleDialog = ref(false)
const showEmailDialog = ref(false)

const statusOptions = [
  { label: 'Shortlist', value: 'shortlisted' as ApplicationStatus },
  { label: 'Reject', value: 'rejected' as ApplicationStatus },
]

function handleStatusChange(event: { value: ApplicationStatus }): void {
  const status = event.value
  const label = status === 'shortlisted' ? 'shortlist' : 'reject'

  confirm.require({
    message: `Are you sure you want to ${label} ${props.candidateName}?`,
    header: 'Confirm Action',
    icon: 'pi pi-exclamation-triangle',
    acceptClass:
      status === 'rejected' ? 'p-button-danger' : 'p-button-success',
    accept: () => emit('statusChange', status),
  })
}
</script>

<template>
  <div class="flex flex-wrap items-center gap-2">
    <Button
      label="Schedule Interview"
      icon="pi pi-calendar-plus"
      size="small"
      severity="info"
      @click="showScheduleDialog = true"
    />
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

    <ScheduleHumanInterviewDialog
      :visible="showScheduleDialog"
      :candidate-id="props.candidateId"
      :candidate-name="props.candidateName"
      @close="showScheduleDialog = false"
    />

    <SendEmailDialog
      :visible="showEmailDialog"
      :candidate-id="props.candidateId"
      :candidate-email="props.candidateEmail"
      @close="showEmailDialog = false"
    />
  </div>
</template>
