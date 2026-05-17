<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const props = withDefaults(
  defineProps<{
    variant?: 'navbar' | 'sidebar'
    collapsed?: boolean
  }>(),
  {
    variant: 'navbar',
    collapsed: false,
  },
)

defineEmits<{
  click: []
}>()

const { t } = useI18n()

const buttonClass = computed(() =>
  props.variant === 'navbar'
    ? 'hidden items-center gap-2 rounded-xl border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-raised)] px-3 py-2 text-left text-xs font-semibold text-[color:var(--color-text-primary)] shadow-sm transition-colors hover:border-[color:var(--color-accent)] hover:bg-[color:var(--color-accent-soft)] sm:flex'
    : 'flex w-full items-center gap-3 rounded-xl border border-[color:var(--color-border-soft)] bg-[color:var(--color-surface-raised)] px-3 py-2.5 text-left text-[13px] font-medium text-[color:var(--color-text-primary)] shadow-sm transition-colors hover:border-[color:var(--color-accent)] hover:bg-[color:var(--color-accent-soft)]',
)
</script>

<template>
  <button
    type="button"
    :class="[buttonClass, collapsed ? 'justify-center' : '']"
    :title="collapsed ? t('aiAssistant.openLabel') : undefined"
    :aria-label="t('aiAssistant.openLabel')"
    @click="$emit('click')"
  >
    <span
      class="flex shrink-0 items-center justify-center rounded-md bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]"
      :class="variant === 'navbar' ? 'h-7 w-7' : 'h-8 w-8'"
    >
      <i class="pi pi-comments" :class="variant === 'navbar' ? 'text-xs' : 'text-sm'"></i>
    </span>
    <span v-if="variant === 'navbar'" class="hidden lg:block">
      <span class="block leading-4">{{ t('aiAssistant.openLabel') }}</span>
      <span class="block text-[10px] font-normal text-[color:var(--color-text-muted)]">
        {{ t('aiAssistant.openHint') }}
      </span>
    </span>
    <span v-else-if="!collapsed" class="min-w-0">
      <span class="block truncate">{{ t('aiAssistant.openLabel') }}</span>
      <span class="block truncate text-[11px] font-normal text-[color:var(--color-text-muted)]">
        {{ t('aiAssistant.openHint') }}
      </span>
    </span>
    <span v-if="variant === 'navbar'" class="lg:hidden">
      {{ t('aiAssistant.openShortLabel') }}
    </span>
  </button>
</template>
