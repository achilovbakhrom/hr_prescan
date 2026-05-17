<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { candidateService } from '../services/candidate.service'

const props = defineProps<{
  candidateId: string
  token: string
}>()

const emit = defineEmits<{
  rotated: [token: string]
}>()

const { t } = useI18n()
const copied = ref(false)
const rotating = ref(false)

async function copyShareLink(): Promise<void> {
  const url = `${window.location.origin}/candidate-review/${props.token}`
  await navigator.clipboard.writeText(url)
  copied.value = true
  window.setTimeout(() => {
    copied.value = false
  }, 2000)
}

async function rotateLink(): Promise<void> {
  rotating.value = true
  try {
    const result = await candidateService.rotateHiringManagerToken(props.candidateId)
    emit('rotated', result.hiringManagerToken)
  } finally {
    rotating.value = false
  }
}
</script>

<template>
  <div class="flex items-center gap-1.5">
    <Button
      :label="
        copied
          ? t('candidates.actions.shareCopied', 'Copied')
          : t('candidates.actions.shareReview', 'Share review')
      "
      icon="pi pi-share-alt"
      size="small"
      severity="secondary"
      outlined
      @click="copyShareLink"
    />
    <Button
      icon="pi pi-refresh"
      size="small"
      severity="secondary"
      outlined
      :loading="rotating"
      :aria-label="t('candidates.actions.rotateShareLink', 'Rotate share link')"
      :title="t('candidates.actions.rotateShareLink', 'Rotate share link')"
      @click="rotateLink"
    />
  </div>
</template>
