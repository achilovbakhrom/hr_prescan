<script setup lang="ts">
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { getLocale } from '@/shared/i18n'
import { translateContent } from '@/shared/api/translate'

const props = defineProps<{
  text: string
  translations: Record<string, string>
  model: string
  objectId: string
  field: string
  /** Use `/translate/` (any auth) instead of `/hr/translate/` (HR-only). */
  scope?: 'hr' | 'public'
}>()

const emit = defineEmits<{
  translated: [translations: Record<string, string>]
}>()

const { t } = useI18n()
const translating = ref(false)

const currentLocale = computed(() => getLocale())

const displayText = computed(() => {
  if (props.translations && props.translations[currentLocale.value]) {
    return props.translations[currentLocale.value]
  }
  return props.text
})

const showTranslateButton = computed(() => {
  if (!props.text) return false
  // Show button whenever current locale's translation is missing
  return !props.translations?.[currentLocale.value]
})

async function handleTranslate() {
  if (translating.value) return
  translating.value = true
  try {
    const result = await translateContent({
      model: props.model,
      objectId: props.objectId,
      field: props.field,
      targetLanguage: currentLocale.value,
      scope: props.scope,
    })
    const updated = { ...props.translations, [result.language]: result.translatedText }
    emit('translated', updated)
  } catch {
    // Translation failed — button stays visible for retry
  } finally {
    translating.value = false
  }
}
</script>

<template>
  <div>
    <slot :text="displayText">
      <p class="whitespace-pre-wrap">{{ displayText }}</p>
    </slot>
    <Button
      v-if="showTranslateButton"
      :label="translating ? t('common.translating') : t('common.translate')"
      icon="pi pi-language"
      severity="secondary"
      size="small"
      text
      :loading="translating"
      class="mt-1.5"
      @click="handleTranslate"
    />
  </div>
</template>
