<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'

const props = defineProps<{
  prescanToken?: string | null
  interviewToken?: string | null
  interviewEnabled?: boolean
}>()

const { t } = useI18n()

const origin = ref('')
const copied = ref<'prescan' | 'interview' | null>(null)

const hasAnyLink = computed(
  () =>
    Boolean(props.prescanToken) || Boolean(props.interviewToken) || Boolean(props.interviewEnabled),
)

onMounted(() => {
  origin.value = window.location.origin
})

function publicUrl(token: string): string {
  return `${origin.value || ''}/interview/${token}`
}

async function copyLink(kind: 'prescan' | 'interview', token: string): Promise<void> {
  const url = publicUrl(token)
  try {
    await navigator.clipboard.writeText(url)
  } catch {
    const input = document.createElement('input')
    input.value = url
    document.body.appendChild(input)
    input.select()
    document.execCommand('copy')
    document.body.removeChild(input)
  }
  copied.value = kind
  setTimeout(() => {
    if (copied.value === kind) copied.value = null
  }, 2000)
}

function openLink(token: string): void {
  window.open(publicUrl(token), '_blank', 'noopener,noreferrer')
}
</script>

<template>
  <div v-if="hasAnyLink" class="border-t border-gray-200 pt-4 dark:border-gray-700">
    <h3 class="text-sm font-semibold text-gray-900 dark:text-gray-100">
      {{ t('candidates.screeningLinks.title') }}
    </h3>

    <div class="mt-3 space-y-3">
      <div v-if="prescanToken" class="space-y-1.5">
        <p class="text-xs font-medium uppercase tracking-wide text-gray-500">
          {{ t('candidates.screeningLinks.prescanning') }}
        </p>
        <div class="flex flex-col gap-2 sm:flex-row">
          <InputText
            :model-value="publicUrl(prescanToken)"
            readonly
            class="min-w-0 flex-1 text-sm"
          />
          <div class="flex gap-2">
            <Button
              icon="pi pi-external-link"
              :label="t('candidates.screeningLinks.open')"
              severity="secondary"
              size="small"
              outlined
              @click="openLink(prescanToken)"
            />
            <Button
              :icon="copied === 'prescan' ? 'pi pi-check' : 'pi pi-copy'"
              :label="copied === 'prescan' ? t('common.copied') : t('common.copyLink')"
              :severity="copied === 'prescan' ? 'success' : 'secondary'"
              size="small"
              @click="copyLink('prescan', prescanToken)"
            />
          </div>
        </div>
      </div>

      <div v-if="interviewToken" class="space-y-1.5">
        <div class="flex flex-wrap items-center gap-2">
          <p class="text-xs font-medium uppercase tracking-wide text-gray-500">
            {{ t('candidates.screeningLinks.interview') }}
          </p>
          <span class="text-xs text-gray-500">
            {{ t('candidates.screeningLinks.interviewLockedHint') }}
          </span>
        </div>
        <div class="flex flex-col gap-2 sm:flex-row">
          <InputText
            :model-value="publicUrl(interviewToken)"
            readonly
            class="min-w-0 flex-1 text-sm"
          />
          <div class="flex gap-2">
            <Button
              icon="pi pi-external-link"
              :label="t('candidates.screeningLinks.open')"
              severity="secondary"
              size="small"
              outlined
              @click="openLink(interviewToken)"
            />
            <Button
              :icon="copied === 'interview' ? 'pi pi-check' : 'pi pi-copy'"
              :label="copied === 'interview' ? t('common.copied') : t('common.copyLink')"
              :severity="copied === 'interview' ? 'success' : 'secondary'"
              size="small"
              @click="copyLink('interview', interviewToken)"
            />
          </div>
        </div>
      </div>

      <div
        v-else-if="interviewEnabled"
        class="rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800"
      >
        {{ t('candidates.screeningLinks.notPrepared') }}
      </div>
    </div>
  </div>
</template>
