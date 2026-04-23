<script setup lang="ts">
/**
 * CompanyDetailHeader — glass header card with logo + name + edit button.
 */
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import GlassCard from '@/shared/components/GlassCard.vue'
import { resolveCountryDisplayName } from '@/shared/constants/countries'
import type { Company } from '../types/company.types'

const props = defineProps<{
  company: Company
  editing: boolean
}>()

defineEmits<{
  edit: []
}>()

const { t, locale } = useI18n()

const countryName = computed(() => resolveCountryDisplayName(props.company.country, locale.value))
</script>

<template>
  <GlassCard>
    <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div class="flex items-center gap-3">
        <div
          v-if="company.logo"
          class="flex h-12 w-12 shrink-0 items-center justify-center overflow-hidden rounded-xl bg-[color:var(--color-surface-sunken)]"
        >
          <img :src="company.logo" :alt="company.name" class="h-full w-full object-contain" />
        </div>
        <div
          v-else
          class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]"
        >
          <i class="pi pi-building text-xl"></i>
        </div>
        <div>
          <h1 class="text-xl font-bold text-[color:var(--color-text-primary)] md:text-2xl">
            {{ company.name }}
          </h1>
          <p v-if="company.country" class="text-xs text-[color:var(--color-text-muted)]">
            {{ countryName }}
          </p>
        </div>
      </div>
      <Button
        v-if="!editing"
        :label="t('common.edit')"
        icon="pi pi-pencil"
        severity="secondary"
        @click="$emit('edit')"
      />
    </div>
  </GlassCard>
</template>
