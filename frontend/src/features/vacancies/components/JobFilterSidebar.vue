<script setup lang="ts">
/**
 * JobFilterSidebar — glass-themed filter panel for the public job board.
 *
 * T13 redesign: thin shell component. Actual form controls live in
 * JobFilterGroups so this file stays small; each layout picks its own
 * outer container.
 */
import { useI18n } from 'vue-i18n'
import GlassSurface from '@/shared/components/GlassSurface.vue'
import JobFilterGroups from './JobFilterGroups.vue'

defineProps<{
  employmentType: string | null
  experienceLevel: string | null
  remoteOnly: boolean
  salaryMin: number | null
  salaryMax: number | null
  activeFilterCount: number
  showMobile?: boolean
}>()

const emit = defineEmits<{
  toggleEmployment: [value: string]
  toggleExperience: [value: string]
  toggleRemote: []
  'update:salaryMin': [value: number | null]
  'update:salaryMax': [value: number | null]
  clearFilters: []
}>()

const { t } = useI18n()
</script>

<template>
  <!-- Desktop sidebar -->
  <aside v-if="!showMobile" class="hidden w-56 shrink-0 lg:block">
    <GlassSurface class="sticky top-4 p-4">
      <div v-if="activeFilterCount > 0" class="mb-4 flex items-center justify-between">
        <span class="text-xs font-medium text-[color:var(--color-text-muted)]">
          {{ activeFilterCount }} {{ t('jobBoard.activeFilters') }}
        </span>
        <button
          class="text-xs text-[color:var(--color-accent)] hover:underline"
          @click="emit('clearFilters')"
        >
          {{ t('jobBoard.clearAll') }}
        </button>
      </div>

      <JobFilterGroups
        layout="desktop"
        :employment-type="employmentType"
        :experience-level="experienceLevel"
        :remote-only="remoteOnly"
        :salary-min="salaryMin"
        :salary-max="salaryMax"
        @toggle-employment="emit('toggleEmployment', $event)"
        @toggle-experience="emit('toggleExperience', $event)"
        @toggle-remote="emit('toggleRemote')"
        @update:salary-min="emit('update:salaryMin', $event)"
        @update:salary-max="emit('update:salaryMax', $event)"
      />
    </GlassSurface>
  </aside>

  <!-- Mobile drawer -->
  <GlassSurface v-else class="mb-4 p-4 lg:hidden">
    <JobFilterGroups
      layout="mobile"
      :employment-type="employmentType"
      :experience-level="experienceLevel"
      :remote-only="remoteOnly"
      :salary-min="salaryMin"
      :salary-max="salaryMax"
      @toggle-employment="emit('toggleEmployment', $event)"
      @toggle-experience="emit('toggleExperience', $event)"
      @toggle-remote="emit('toggleRemote')"
      @update:salary-min="emit('update:salaryMin', $event)"
      @update:salary-max="emit('update:salaryMax', $event)"
    />
  </GlassSurface>
</template>
