<script setup lang="ts">
import { ref } from 'vue'
import Calendar from 'primevue/calendar'
import Button from 'primevue/button'

defineProps<{
  loading: boolean
  vacancyTitle?: string
  durationMinutes?: number
}>()

const emit = defineEmits<{
  submit: [scheduledAt: string]
}>()

const selectedDate = ref<Date | null>(null)
const minDate = ref(new Date())

function handleSubmit(): void {
  if (!selectedDate.value) return
  emit('submit', selectedDate.value.toISOString())
}
</script>

<template>
  <form class="space-y-6" @submit.prevent="handleSubmit">
    <div v-if="vacancyTitle" class="rounded-lg bg-blue-50 p-4">
      <p class="text-sm text-gray-600">Position</p>
      <p class="text-lg font-semibold text-gray-900">{{ vacancyTitle }}</p>
      <p v-if="durationMinutes" class="mt-1 text-sm text-gray-500">
        Duration: {{ durationMinutes }} minutes
      </p>
    </div>

    <div>
      <label class="mb-2 block text-sm font-medium text-gray-700">
        Select Date and Time
      </label>
      <Calendar
        v-model="selectedDate"
        :min-date="minDate"
        show-time
        hour-format="24"
        :step-minute="15"
        :manual-input="false"
        placeholder="Pick a date and time"
        class="w-full"
        date-format="dd/mm/yy"
      />
    </div>

    <Button
      type="submit"
      label="Schedule Interview"
      icon="pi pi-calendar-plus"
      :loading="loading"
      :disabled="!selectedDate"
      class="w-full"
    />
  </form>
</template>
