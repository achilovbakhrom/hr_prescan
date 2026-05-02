<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import Dialog from 'primevue/dialog'
import Calendar from 'primevue/calendar'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'
import { candidateService } from '../services/candidate.service'

const props = defineProps<{
  visible: boolean
  candidateId: string
  candidateName: string
}>()

const emit = defineEmits<{
  close: []
}>()

const dateTime = ref<Date | null>(null)
const interviewerName = ref('')
const meetingLink = ref('')
const submitting = ref(false)
const submitted = ref(false)
const { t } = useI18n()

watch(
  () => props.visible,
  (val) => {
    if (val) {
      dateTime.value = null
      interviewerName.value = ''
      meetingLink.value = ''
      submitted.value = false
    }
  },
)

async function handleSubmit(): Promise<void> {
  if (!dateTime.value || !interviewerName.value.trim()) return

  submitting.value = true
  try {
    await candidateService.scheduleHumanInterview(props.candidateId, {
      dateTime: dateTime.value.toISOString(),
      interviewerName: interviewerName.value,
      meetingLink: meetingLink.value || undefined,
    })
    submitted.value = true
    setTimeout(() => emit('close'), 1500)
  } catch {
    // Silently fail
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <Dialog
    :visible="props.visible"
    :header="t('candidates.humanInterview.title')"
    :modal="true"
    :closable="true"
    :style="{ width: '500px' }"
    @update:visible="emit('close')"
  >
    <div v-if="submitted" class="py-4 text-center">
      <i class="pi pi-check-circle mb-2 text-3xl text-green-500"></i>
      <p class="text-sm text-gray-700">
        {{ t('candidates.humanInterview.scheduledFor', { name: props.candidateName }) }}
      </p>
    </div>

    <div v-else class="space-y-4">
      <p class="text-sm text-gray-500">
        {{ t('candidates.humanInterview.schedulingFor', { name: props.candidateName }) }}
      </p>

      <div>
        <label class="mb-1 block text-sm font-medium text-gray-700">
          {{ t('candidates.humanInterview.dateTime') }}
        </label>
        <Calendar
          v-model="dateTime"
          show-time
          hour-format="24"
          :min-date="new Date()"
          class="w-full"
          :placeholder="t('candidates.humanInterview.dateTimePlaceholder')"
        />
      </div>

      <div>
        <label class="mb-1 block text-sm font-medium text-gray-700">
          {{ t('candidates.humanInterview.interviewerName') }}
        </label>
        <InputText
          v-model="interviewerName"
          class="w-full"
          :placeholder="t('candidates.humanInterview.interviewerPlaceholder')"
        />
      </div>

      <div>
        <label class="mb-1 block text-sm font-medium text-gray-700">
          {{ t('candidates.humanInterview.meetingLink') }}
        </label>
        <InputText
          v-model="meetingLink"
          class="w-full"
          :placeholder="t('candidates.humanInterview.meetingLinkPlaceholder')"
        />
      </div>
    </div>

    <template #footer>
      <div v-if="!submitted" class="flex justify-end gap-2">
        <Button :label="t('common.cancel')" severity="secondary" text @click="emit('close')" />
        <Button
          :label="t('candidates.humanInterview.schedule')"
          icon="pi pi-calendar-plus"
          :loading="submitting"
          :disabled="!dateTime || !interviewerName.trim()"
          @click="handleSubmit"
        />
      </div>
    </template>
  </Dialog>
</template>
