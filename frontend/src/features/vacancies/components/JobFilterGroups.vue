<script setup lang="ts">
/**
 * JobFilterGroups — shared filter controls for JobFilterSidebar's
 * desktop + mobile renderings. Takes a `layout` prop so each shell can
 * style its own outer container.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import InputNumber from 'primevue/inputnumber'

const props = defineProps<{
  employmentType: string | null
  experienceLevel: string | null
  remoteOnly: boolean
  salaryMin: number | null
  salaryMax: number | null
  layout: 'desktop' | 'mobile'
}>()

const emit = defineEmits<{
  toggleEmployment: [value: string]
  toggleExperience: [value: string]
  toggleRemote: []
  'update:salaryMin': [value: number | null]
  'update:salaryMax': [value: number | null]
}>()

const { t } = useI18n()

const employmentOptions = computed(() => [
  { value: 'full_time', label: t('vacancies.employment.fullTime'), icon: 'pi pi-clock' },
  { value: 'part_time', label: t('vacancies.employment.partTime'), icon: 'pi pi-hourglass' },
  { value: 'contract', label: t('vacancies.employment.contract'), icon: 'pi pi-file' },
  {
    value: 'internship',
    label: t('vacancies.employment.internship'),
    icon: 'pi pi-graduation-cap',
  },
])

const experienceOptions = computed(() => [
  { value: 'junior', label: t('vacancies.experience.junior') },
  { value: 'middle', label: t('vacancies.experience.middle') },
  { value: 'senior', label: t('vacancies.experience.senior') },
  { value: 'lead', label: t('vacancies.experience.lead') },
  { value: 'director', label: t('vacancies.experience.director') },
])

const isDesktop = computed(() => props.layout === 'desktop')
</script>

<template>
  <div :class="isDesktop ? 'space-y-5' : 'space-y-4'">
    <div>
      <button
        class="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm font-medium ease-ios transition-colors"
        :class="
          remoteOnly
            ? 'bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]'
            : 'text-[color:var(--color-text-secondary)] hover:bg-[color:var(--color-surface-raised)]'
        "
        @click="emit('toggleRemote')"
      >
        <i class="pi pi-globe text-sm"></i>
        {{ t('jobBoard.remoteOnly') }}
      </button>
    </div>

    <div>
      <h3
        class="mb-2 text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
      >
        {{ t('vacancies.form.employmentType') }}
      </h3>
      <div v-if="isDesktop" class="space-y-1">
        <button
          v-for="opt in employmentOptions"
          :key="opt.value"
          class="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm ease-ios transition-colors"
          :class="
            employmentType === opt.value
              ? 'bg-[color:var(--color-accent-soft)] font-medium text-[color:var(--color-accent)]'
              : 'text-[color:var(--color-text-secondary)] hover:bg-[color:var(--color-surface-raised)]'
          "
          @click="emit('toggleEmployment', opt.value)"
        >
          <i :class="opt.icon" class="text-xs"></i>
          {{ opt.label }}
        </button>
      </div>
      <div v-else class="flex flex-wrap gap-2">
        <button
          v-for="opt in employmentOptions"
          :key="opt.value"
          class="rounded-full border px-3 py-1.5 text-xs font-medium ease-ios transition-colors"
          :class="
            employmentType === opt.value
              ? 'border-[color:var(--color-accent)] bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]'
              : 'border-[color:var(--color-border-soft)] text-[color:var(--color-text-secondary)]'
          "
          @click="emit('toggleEmployment', opt.value)"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <div>
      <h3
        class="mb-2 text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
      >
        {{ t('vacancies.form.experienceLevel') }}
      </h3>
      <div v-if="isDesktop" class="space-y-1">
        <button
          v-for="opt in experienceOptions"
          :key="opt.value"
          class="flex w-full items-center gap-2 rounded-md px-3 py-2 text-sm ease-ios transition-colors"
          :class="
            experienceLevel === opt.value
              ? 'bg-[color:var(--color-accent-soft)] font-medium text-[color:var(--color-accent)]'
              : 'text-[color:var(--color-text-secondary)] hover:bg-[color:var(--color-surface-raised)]'
          "
          @click="emit('toggleExperience', opt.value)"
        >
          {{ opt.label }}
        </button>
      </div>
      <div v-else class="flex flex-wrap gap-2">
        <button
          v-for="opt in experienceOptions"
          :key="opt.value"
          class="rounded-full border px-3 py-1.5 text-xs font-medium ease-ios transition-colors"
          :class="
            experienceLevel === opt.value
              ? 'border-[color:var(--color-accent)] bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]'
              : 'border-[color:var(--color-border-soft)] text-[color:var(--color-text-secondary)]'
          "
          @click="emit('toggleExperience', opt.value)"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <div>
      <h3
        class="mb-2 text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
      >
        {{ t('jobBoard.salaryRange') }}
      </h3>
      <div :class="isDesktop ? 'space-y-2' : 'flex gap-2'">
        <InputNumber
          :model-value="salaryMin"
          :placeholder="t('jobBoard.minSalary')"
          :min="0"
          mode="decimal"
          :use-grouping="true"
          :class="isDesktop ? 'w-full' : 'flex-1'"
          input-class="w-full text-sm"
          @update:model-value="emit('update:salaryMin', $event as number | null)"
        />
        <InputNumber
          :model-value="salaryMax"
          :placeholder="t('jobBoard.maxSalary')"
          :min="0"
          mode="decimal"
          :use-grouping="true"
          :class="isDesktop ? 'w-full' : 'flex-1'"
          input-class="w-full text-sm"
          @update:model-value="emit('update:salaryMax', $event as number | null)"
        />
      </div>
    </div>
  </div>
</template>
