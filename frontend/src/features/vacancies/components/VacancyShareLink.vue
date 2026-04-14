<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import InputText from 'primevue/inputtext'
import Button from 'primevue/button'

const props = defineProps<{
  shareToken: string
}>()

const { t } = useI18n()

const copied = ref(false)

const shareUrl = computed(() => {
  const base = window.location.origin
  return `${base}/jobs/share/${props.shareToken}`
})

async function copyLink(): Promise<void> {
  try {
    await navigator.clipboard.writeText(shareUrl.value)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch {
    // Fallback for older browsers
    const input = document.createElement('input')
    input.value = shareUrl.value
    document.body.appendChild(input)
    input.select()
    document.execCommand('copy')
    document.body.removeChild(input)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  }
}
</script>

<template>
  <div class="flex items-center gap-2">
    <InputText :model-value="shareUrl" readonly class="flex-1 text-sm" />
    <Button
      :icon="copied ? 'pi pi-check' : 'pi pi-copy'"
      :label="copied ? t('common.copied') : t('common.copyLink')"
      :severity="copied ? 'success' : 'secondary'"
      size="small"
      @click="copyLink"
    />
  </div>
</template>
