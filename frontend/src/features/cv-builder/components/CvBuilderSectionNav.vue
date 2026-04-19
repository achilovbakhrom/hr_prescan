<script setup lang="ts">
/**
 * CvBuilderSectionNav — left rail of CV sections.
 * Glass pill per section with active state + completeness dot.
 */
import { useI18n } from 'vue-i18n'
import GlassSurface from '@/shared/components/GlassSurface.vue'
import type { Completeness } from '../types/cv-builder.types'

interface Section {
  id: string
  labelKey: string
  icon: string
  doneKey: keyof Completeness['sections']
}

defineProps<{
  activeId: string
  completeness?: Completeness
}>()

const emit = defineEmits<{
  select: [id: string]
}>()

const { t } = useI18n()

const sections: Section[] = [
  { id: '0', labelKey: 'cvBuilder.tabs.personal', icon: 'pi pi-user', doneKey: 'personal' },
  {
    id: '1',
    labelKey: 'cvBuilder.tabs.experience',
    icon: 'pi pi-briefcase',
    doneKey: 'experience',
  },
  {
    id: '2',
    labelKey: 'cvBuilder.tabs.education',
    icon: 'pi pi-graduation-cap',
    doneKey: 'education',
  },
  { id: '3', labelKey: 'cvBuilder.tabs.skills', icon: 'pi pi-star', doneKey: 'skills' },
  { id: '4', labelKey: 'cvBuilder.tabs.languages', icon: 'pi pi-globe', doneKey: 'languages' },
  {
    id: '5',
    labelKey: 'cvBuilder.tabs.certifications',
    icon: 'pi pi-verified',
    doneKey: 'personal',
  },
]
</script>

<template>
  <GlassSurface level="1" class="sticky top-6 rounded-lg p-3">
    <span
      class="block px-3 pt-2 pb-3 text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
    >
      {{ t('cvBuilder.sections') || 'Sections' }}
    </span>
    <nav class="flex flex-col gap-1" role="tablist">
      <button
        v-for="sec in sections"
        :key="sec.id"
        type="button"
        role="tab"
        :aria-selected="activeId === sec.id"
        :class="[
          'section-nav-btn',
          activeId === sec.id ? 'section-nav-btn--active' : 'section-nav-btn--inactive',
        ]"
        @click="emit('select', sec.id)"
      >
        <i :class="[sec.icon, 'w-4 text-center text-sm']"></i>
        <span class="flex-1 truncate text-left">{{ t(sec.labelKey) }}</span>
        <span
          v-if="completeness && completeness.sections[sec.doneKey]"
          class="inline-block h-1.5 w-1.5 rounded-full bg-[color:var(--color-success)]"
          aria-label="complete"
        ></span>
      </button>
    </nav>
  </GlassSurface>
</template>

<style scoped>
.section-nav-btn {
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
.section-nav-btn:hover {
  background: var(--color-surface-sunken);
  color: var(--color-text-primary);
}
.section-nav-btn--active {
  background: var(--color-accent-soft) !important;
  color: var(--color-accent) !important;
}
.section-nav-btn:focus-visible {
  outline: 2px solid var(--color-border-ring);
  outline-offset: 2px;
}
</style>
