<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

interface ConversationMessage {
  role: 'ai' | 'candidate'
  text: string
  timestamp?: string | number | null
}

const props = defineProps<{
  messages: ConversationMessage[]
}>()

const { t } = useI18n()

function unclearSegmentsLabel(count: number): string {
  const translated = t('interviews.qualityUnclearSegments', { count })
  return translated === 'interviews.qualityUnclearSegments'
    ? `${count} unclear segment${count > 1 ? 's' : ''}`
    : translated
}

const indicators = computed(() => {
  const items: Array<{ label: string; tone: string }> = []
  const candidateMessages = props.messages.filter((message) => message.role === 'candidate')
  const unclearCount = props.messages.filter((message) =>
    /\b(inaudible|unclear|unintelligible|неразборчиво)\b/i.test(message.text),
  ).length
  const hasNumericTimestamps = props.messages.some(
    (message) => typeof message.timestamp === 'number',
  )

  if (props.messages.length < 4) {
    items.push({
      label: t('interviews.qualityShortTranscript', 'Short transcript'),
      tone: 'yellow',
    })
  }
  if (unclearCount) {
    items.push({
      label: unclearSegmentsLabel(unclearCount),
      tone: 'red',
    })
  }
  if (!hasNumericTimestamps) {
    items.push({
      label: t('interviews.qualityNoTimestamps', 'No recording timestamps'),
      tone: 'gray',
    })
  }
  if (candidateMessages.length && candidateMessages.every((message) => message.text.length < 80)) {
    items.push({
      label: t('interviews.qualityBriefAnswers', 'Mostly brief answers'),
      tone: 'yellow',
    })
  }

  return items
})

function toneClass(tone: string): string {
  if (tone === 'red') return 'bg-red-50 text-red-700 ring-red-200'
  if (tone === 'yellow') return 'bg-yellow-50 text-yellow-700 ring-yellow-200'
  return 'bg-gray-50 text-gray-600 ring-gray-200'
}
</script>

<template>
  <div v-if="indicators.length" class="flex flex-wrap gap-2">
    <span
      v-for="item in indicators"
      :key="item.label"
      class="rounded-full px-2.5 py-1 text-xs font-medium ring-1"
      :class="toneClass(item.tone)"
    >
      {{ item.label }}
    </span>
  </div>
</template>
