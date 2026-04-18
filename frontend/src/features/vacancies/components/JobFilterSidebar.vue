<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import InputNumber from 'primevue/inputnumber'

const props = defineProps<{
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
</script>

<template>
  <!-- Desktop sidebar -->
  <aside v-if="!showMobile" class="hidden w-56 shrink-0 lg:block">
    <div class="sticky top-4 space-y-6">
      <div v-if="activeFilterCount > 0" class="flex items-center justify-between">
        <span class="text-xs font-medium text-gray-500"
          >{{ activeFilterCount }} {{ t('jobBoard.activeFilters') }}</span
        >
        <button class="text-xs text-blue-600 hover:underline" @click="emit('clearFilters')">
          {{ t('jobBoard.clearAll') }}
        </button>
      </div>

      <div>
        <button
          class="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors"
          :class="remoteOnly ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-gray-100'"
          @click="emit('toggleRemote')"
        >
          <i class="pi pi-globe text-sm"></i>
          {{ t('jobBoard.remoteOnly') }}
        </button>
      </div>

      <div>
        <h3 class="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400">
          {{ t('vacancies.form.employmentType') }}
        </h3>
        <div class="space-y-1">
          <button
            v-for="opt in employmentOptions"
            :key="opt.value"
            class="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors"
            :class="
              employmentType === opt.value
                ? 'bg-blue-50 font-medium text-blue-700'
                : 'text-gray-600 hover:bg-gray-100'
            "
            @click="emit('toggleEmployment', opt.value)"
          >
            <i :class="opt.icon" class="text-xs"></i>
            {{ opt.label }}
          </button>
        </div>
      </div>

      <div>
        <h3 class="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400">
          {{ t('vacancies.form.experienceLevel') }}
        </h3>
        <div class="space-y-1">
          <button
            v-for="opt in experienceOptions"
            :key="opt.value"
            class="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors"
            :class="
              experienceLevel === opt.value
                ? 'bg-blue-50 font-medium text-blue-700'
                : 'text-gray-600 hover:bg-gray-100'
            "
            @click="emit('toggleExperience', opt.value)"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>

      <div>
        <h3 class="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400">
          {{ t('jobBoard.salaryRange') }}
        </h3>
        <div class="space-y-2">
          <InputNumber
            :model-value="salaryMin"
            :placeholder="t('jobBoard.minSalary')"
            :min="0"
            mode="decimal"
            :use-grouping="true"
            class="w-full"
            input-class="w-full text-sm"
            @update:model-value="emit('update:salaryMin', $event as number | null)"
          />
          <InputNumber
            :model-value="salaryMax"
            :placeholder="t('jobBoard.maxSalary')"
            :min="0"
            mode="decimal"
            :use-grouping="true"
            class="w-full"
            input-class="w-full text-sm"
            @update:model-value="emit('update:salaryMax', $event as number | null)"
          />
        </div>
      </div>
    </div>
  </aside>

  <!-- Mobile filter drawer -->
  <div v-else class="mb-4 space-y-4 rounded-xl border border-gray-200 bg-white p-4 lg:hidden">
    <button
      class="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors"
      :class="remoteOnly ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-gray-100'"
      @click="emit('toggleRemote')"
    >
      <i class="pi pi-globe text-sm"></i>
      {{ t('jobBoard.remoteOnly') }}
    </button>

    <div>
      <p class="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400">
        {{ t('vacancies.form.employmentType') }}
      </p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="opt in employmentOptions"
          :key="opt.value"
          class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
          :class="
            employmentType === opt.value
              ? 'border-blue-200 bg-blue-50 text-blue-700'
              : 'border-gray-200 text-gray-600'
          "
          @click="emit('toggleEmployment', opt.value)"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <div>
      <p class="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400">
        {{ t('vacancies.form.experienceLevel') }}
      </p>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="opt in experienceOptions"
          :key="opt.value"
          class="rounded-full border px-3 py-1.5 text-xs font-medium transition-colors"
          :class="
            experienceLevel === opt.value
              ? 'border-blue-200 bg-blue-50 text-blue-700'
              : 'border-gray-200 text-gray-600'
          "
          @click="emit('toggleExperience', opt.value)"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <div>
      <p class="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400">
        {{ t('jobBoard.salaryRange') }}
      </p>
      <div class="flex gap-2">
        <InputNumber
          :model-value="props.salaryMin"
          :placeholder="t('jobBoard.minSalary')"
          :min="0"
          mode="decimal"
          :use-grouping="true"
          class="flex-1"
          input-class="w-full text-sm"
          @update:model-value="emit('update:salaryMin', $event as number | null)"
        />
        <InputNumber
          :model-value="props.salaryMax"
          :placeholder="t('jobBoard.maxSalary')"
          :min="0"
          mode="decimal"
          :use-grouping="true"
          class="flex-1"
          input-class="w-full text-sm"
          @update:model-value="emit('update:salaryMax', $event as number | null)"
        />
      </div>
    </div>
  </div>
</template>
