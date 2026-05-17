<script setup lang="ts">
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import Textarea from 'primevue/textarea'
import Button from 'primevue/button'
import ApplicationEventList from './ApplicationEventList.vue'
import HiringManagerFeedbackList from './HiringManagerFeedbackList.vue'
import type { ApplicationEvent, HiringManagerFeedback } from '../types/candidate.types'

const props = defineProps<{
  notes: string
  loading: boolean
  hiringManagerFeedback?: HiringManagerFeedback[]
  events?: ApplicationEvent[]
}>()

const emit = defineEmits<{
  save: [note: string]
}>()

const { t } = useI18n()

const localNotes = ref(props.notes)

watch(
  () => props.notes,
  (val) => {
    localNotes.value = val
  },
)

function handleSave(): void {
  emit('save', localNotes.value)
}
</script>

<template>
  <div class="space-y-3">
    <ApplicationEventList :events="events || []" />
    <div class="border-t border-gray-200 pt-3 dark:border-gray-700"></div>
    <HiringManagerFeedbackList :feedback="hiringManagerFeedback || []" />
    <div class="border-t border-gray-200 pt-3 dark:border-gray-700"></div>
    <h3 class="text-sm font-semibold text-gray-600">{{ t('candidates.notes') }}</h3>
    <Textarea
      v-model="localNotes"
      rows="6"
      class="w-full"
      :placeholder="t('candidates.notesPlaceholder')"
      :disabled="props.loading"
    />
    <div class="flex justify-end">
      <Button
        :label="t('common.save')"
        icon="pi pi-save"
        size="small"
        :loading="props.loading"
        @click="handleSave"
      />
    </div>
  </div>
</template>
