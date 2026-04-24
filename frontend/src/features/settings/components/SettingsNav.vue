<script setup lang="ts">
/**
 * SettingsNav — sticky left rail for settings pages.
 * Glass surface with pill-per-section. Scrolls to section on click.
 */
import { useI18n } from 'vue-i18n'
import GlassSurface from '@/shared/components/GlassSurface.vue'

interface NavItem {
  id: string
  labelKey: string
  icon: string
}

defineProps<{
  activeId: string
  items: NavItem[]
}>()

const emit = defineEmits<{
  select: [id: string]
}>()

const { t } = useI18n()
</script>

<template>
  <GlassSurface level="1" class="sticky top-6 rounded-lg p-3">
    <span
      class="block px-3 pt-2 pb-3 text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
    >
      {{ t('settings.sections') }}
    </span>
    <nav class="flex flex-col gap-1">
      <button
        v-for="item in items"
        :key="item.id"
        type="button"
        :class="[
          'settings-nav-btn',
          activeId === item.id ? 'settings-nav-btn--active' : 'settings-nav-btn--inactive',
        ]"
        @click="emit('select', item.id)"
      >
        <i :class="[item.icon, 'w-4 text-center text-sm']"></i>
        <span class="flex-1 truncate text-left">{{ t(item.labelKey) }}</span>
      </button>
    </nav>
  </GlassSurface>
</template>

<style scoped>
.settings-nav-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-weight: 500;
  transition:
    background-color 180ms var(--ease-ios),
    color 180ms var(--ease-ios);
  cursor: pointer;
  color: var(--color-text-secondary);
}
.settings-nav-btn:hover {
  background: var(--color-surface-sunken);
  color: var(--color-text-primary);
}
.settings-nav-btn--active {
  background: var(--color-accent-soft) !important;
  color: var(--color-accent) !important;
}
.settings-nav-btn:focus-visible {
  outline: 2px solid var(--color-border-ring);
  outline-offset: 2px;
}
</style>
