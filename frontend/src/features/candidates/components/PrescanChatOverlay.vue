<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'

defineProps<{
  showOverlay: boolean
  prescanToken: string | null
  chatUrl: string
  showMinimized: boolean
}>()

const emit = defineEmits<{
  openFullScreen: []
  minimize: []
  restore: []
  dismiss: []
  completed: []
}>()

const { t } = useI18n()

function onMessage(event: MessageEvent): void {
  if (event.data?.type === 'prescan_completed') {
    emit('completed')
  }
}

onMounted(() => window.addEventListener('message', onMessage))
onUnmounted(() => window.removeEventListener('message', onMessage))
</script>

<template>
  <!-- Chat overlay -->
  <div
    v-if="showOverlay && prescanToken"
    class="fixed inset-0 z-50 flex flex-col bg-black/30 backdrop-blur-sm sm:items-center sm:justify-center sm:p-4"
  >
    <div
      class="flex h-full w-full flex-col overflow-hidden bg-white dark:bg-gray-800 sm:h-[85vh] sm:max-h-[700px] sm:max-w-3xl sm:rounded-2xl sm:shadow-2xl"
    >
      <div
        class="flex items-center justify-between bg-gradient-to-r from-blue-600 to-blue-700 px-3 py-2.5 sm:px-4 sm:py-3"
      >
        <div class="flex items-center gap-2 sm:gap-3">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-full bg-white/20 ring-2 ring-white/30 sm:h-10 sm:w-10"
          >
            <i class="pi pi-comments text-xs text-white sm:text-sm"></i>
          </div>
          <div class="min-w-0">
            <p class="truncate text-xs font-semibold text-white sm:text-sm">
              {{ t('interviews.chat.aiPrescanning') }}
            </p>
            <p class="hidden text-xs text-blue-100 sm:block">
              {{ t('candidates.application.answerQuestions') }}
            </p>
          </div>
        </div>
        <div class="flex items-center gap-0.5 sm:gap-1">
          <Button
            icon="pi pi-external-link"
            severity="secondary"
            text
            rounded
            size="small"
            class="!h-8 !w-8 !text-white/70 hover:!bg-white/10 hover:!text-white sm:!h-9 sm:!w-9"
            @click="emit('openFullScreen')"
          />
          <Button
            icon="pi pi-minus"
            severity="secondary"
            text
            rounded
            size="small"
            class="!h-8 !w-8 !text-white/70 hover:!bg-white/10 hover:!text-white sm:!h-9 sm:!w-9"
            @click="emit('minimize')"
          />
        </div>
      </div>
      <iframe :src="chatUrl" class="min-h-0 flex-1 border-0" allow="microphone; camera"></iframe>
    </div>
  </div>

  <!-- Minimized chat bar -->
  <div
    v-if="showMinimized"
    class="fixed bottom-0 left-0 right-0 z-40 cursor-pointer border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2.5 shadow-lg transition-all hover:bg-gray-50 dark:hover:bg-gray-800 sm:px-4 sm:py-3"
    @click="emit('restore')"
  >
    <div class="mx-auto flex max-w-3xl items-center justify-between">
      <div class="flex items-center gap-2 sm:gap-3">
        <div
          class="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 dark:bg-blue-700 sm:h-10 sm:w-10"
        >
          <i class="pi pi-comments text-xs text-white sm:text-sm"></i>
        </div>
        <div class="min-w-0">
          <p class="truncate text-xs font-medium text-gray-900 dark:text-white sm:text-sm">
            {{ t('interviews.chat.aiPrescanning') }}
          </p>
          <p class="hidden text-xs text-gray-500 dark:text-gray-400 sm:block">
            {{ t('candidates.application.clickToOpenChat') }}
          </p>
        </div>
      </div>
      <div class="flex items-center gap-1 sm:gap-2">
        <i class="pi pi-chevron-up text-xs text-gray-400 dark:text-gray-500 sm:text-sm"></i>
        <Button
          icon="pi pi-times"
          severity="secondary"
          text
          rounded
          size="small"
          class="!h-8 !w-8 sm:!h-9 sm:!w-9"
          @click.stop="emit('dismiss')"
        />
      </div>
    </div>
  </div>
</template>
