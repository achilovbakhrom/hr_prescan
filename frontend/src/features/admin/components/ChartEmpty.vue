<script setup lang="ts">
import { useI18n } from 'vue-i18n'
const { t } = useI18n()
</script>

<template>
  <div
    class="flex h-full items-center justify-center rounded bg-[color:var(--color-surface-raised)]"
  >
    <p class="text-xs text-[color:var(--color-text-muted)]">{{ t('common.noData') }}</p>
  </div>
</template>
