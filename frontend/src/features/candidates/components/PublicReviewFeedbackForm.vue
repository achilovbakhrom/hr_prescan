<script setup lang="ts">
import { ref } from 'vue'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import AppSelect from '@/shared/components/AppSelect.vue'
import { candidateService } from '../services/candidate.service'

const props = defineProps<{
  token: string
}>()

const reviewerName = ref('')
const reviewerRole = ref('')
const recommendation = ref<'advance' | 'maybe' | 'reject'>('maybe')
const rating = ref<number | null>(null)
const comment = ref('')
const loading = ref(false)
const submitted = ref(false)
const error = ref('')

const recommendationOptions = [
  { label: 'Advance', value: 'advance' },
  { label: 'Maybe', value: 'maybe' },
  { label: 'Reject', value: 'reject' },
]
const ratingOptions = [1, 2, 3, 4, 5].map((value) => ({ label: `${value}/5`, value }))

async function submitFeedback(): Promise<void> {
  if (!reviewerName.value.trim()) {
    error.value = 'Reviewer name is required.'
    return
  }
  loading.value = true
  error.value = ''
  try {
    await candidateService.submitHiringManagerFeedback(props.token, {
      reviewerName: reviewerName.value,
      reviewerRole: reviewerRole.value,
      recommendation: recommendation.value,
      rating: rating.value,
      comment: comment.value,
    })
    submitted.value = true
  } catch {
    error.value = 'Feedback could not be submitted.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <div v-if="submitted" class="rounded-lg bg-green-50 p-4 text-sm text-green-700">
      Feedback submitted.
    </div>
    <form v-else class="space-y-3" @submit.prevent="submitFeedback">
      <h2 class="text-sm font-semibold text-gray-700">Hiring manager feedback</h2>
      <div class="grid gap-3 sm:grid-cols-2">
        <InputText v-model="reviewerName" placeholder="Your name" />
        <InputText v-model="reviewerRole" placeholder="Role or team" />
      </div>
      <div class="grid gap-3 sm:grid-cols-2">
        <AppSelect
          v-model="recommendation"
          :options="recommendationOptions"
          option-label="label"
          option-value="value"
        />
        <AppSelect
          v-model="rating"
          :options="ratingOptions"
          option-label="label"
          option-value="value"
          placeholder="Rating"
          show-clear
        />
      </div>
      <Textarea v-model="comment" rows="4" class="w-full" placeholder="Feedback for HR" />
      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
      <div class="flex justify-end">
        <Button label="Submit feedback" icon="pi pi-send" type="submit" :loading="loading" />
      </div>
    </form>
  </div>
</template>
