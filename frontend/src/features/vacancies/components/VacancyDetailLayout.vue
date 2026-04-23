<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Dropdown from '@/shared/components/AppSelect.vue'
import GlassCard from '@/shared/components/GlassCard.vue'
import VacancyStatusBadge from './VacancyStatusBadge.vue'
import type { VacancyDetail } from '../types/vacancy.types'

interface RailItem {
  key: string
  label: string
  icon: string
  count?: number | null
}

const props = defineProps<{
  vacancy: VacancyDetail
  active: string
  candidatesTotal: number
  candidatesShortlisted: number
}>()

const emit = defineEmits<{
  navigate: [key: string]
}>()

const { t } = useI18n()

const items = computed<RailItem[]>(() => {
  const list: RailItem[] = [
    { key: 'details', label: t('vacancies.section.details'), icon: 'pi pi-info-circle' },
    {
      key: 'prescanning',
      label: t('vacancies.form.prescanning'),
      icon: 'pi pi-comments',
      count: props.vacancy.questions?.filter((q) => q.step === 'prescanning').length ?? 0,
    },
  ]
  if (props.vacancy.interviewEnabled) {
    list.push({
      key: 'interview',
      label: t('vacancies.form.interview'),
      icon: 'pi pi-video',
      count: props.vacancy.questions?.filter((q) => q.step === 'interview').length ?? 0,
    })
  }
  list.push({
    key: 'candidates',
    label: t('candidates.title'),
    icon: 'pi pi-users',
    count: props.candidatesTotal,
  })
  list.push({ key: 'settings', label: t('nav.settings'), icon: 'pi pi-cog' })
  return list
})

const dropdownOptions = computed(() => items.value.map((i) => ({ label: i.label, value: i.key })))

function selectMobile(e: { value: string }): void {
  emit('navigate', e.value)
}
</script>

<template>
  <div>
    <!-- Mobile: section dropdown selector -->
    <div class="mb-4 lg:hidden">
      <Dropdown
        :model-value="active"
        :options="dropdownOptions"
        option-label="label"
        option-value="value"
        class="w-full"
        @change="selectMobile"
      />
    </div>

    <div class="flex flex-col gap-6 lg:flex-row">
      <!-- Desktop: left rail -->
      <aside class="hidden w-56 shrink-0 lg:block">
        <div class="sticky top-4 space-y-4">
          <!-- At a glance card -->
          <GlassCard class="!p-4">
            <p
              class="mb-2 text-[10px] font-semibold uppercase tracking-widest text-[color:var(--color-text-muted)]"
            >
              {{ t('vacancies.atAGlance') }}
            </p>
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-xs text-[color:var(--color-text-muted)]">{{
                  t('common.status')
                }}</span>
                <VacancyStatusBadge :status="vacancy.status" />
              </div>
              <div class="flex items-center justify-between">
                <span class="text-xs text-[color:var(--color-text-muted)]">{{
                  t('vacancies.applied')
                }}</span>
                <span
                  class="font-mono text-sm font-semibold text-[color:var(--color-text-primary)]"
                  >{{ candidatesTotal }}</span
                >
              </div>
              <div class="flex items-center justify-between">
                <span class="text-xs text-[color:var(--color-text-muted)]">{{
                  t('vacancies.shortlisted')
                }}</span>
                <span
                  class="font-mono text-sm font-semibold text-[color:var(--color-text-primary)]"
                  >{{ candidatesShortlisted }}</span
                >
              </div>
            </div>
          </GlassCard>

          <!-- Section nav -->
          <GlassCard class="!p-2">
            <nav>
              <button
                v-for="item in items"
                :key="item.key"
                type="button"
                class="flex w-full items-center gap-3 rounded-md px-3 py-2 text-left text-sm font-medium transition-colors"
                :class="
                  active === item.key
                    ? 'bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]'
                    : 'text-[color:var(--color-text-secondary)] hover:bg-[color:var(--color-surface-sunken)] hover:text-[color:var(--color-text-primary)]'
                "
                @click="emit('navigate', item.key)"
              >
                <i
                  :class="item.icon"
                  class="text-sm"
                  :style="{ width: '16px', textAlign: 'center' }"
                ></i>
                <span class="flex-1 truncate">{{ item.label }}</span>
                <span
                  v-if="item.count != null"
                  class="rounded-full bg-[color:var(--color-surface-sunken)] px-2 py-0.5 text-[10px] font-semibold text-[color:var(--color-text-muted)]"
                  >{{ item.count }}</span
                >
              </button>
            </nav>
          </GlassCard>
        </div>
      </aside>

      <!-- Main content -->
      <div class="min-w-0 flex-1">
        <slot />
      </div>
    </div>
  </div>
</template>
