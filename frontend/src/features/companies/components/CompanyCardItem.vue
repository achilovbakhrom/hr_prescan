<script setup lang="ts">
/**
 * CompanyCardItem — single glass card for the companies grid.
 * Extracted from CompanyListPage to respect the 200-line file cap.
 */
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import GlassCard from '@/shared/components/GlassCard.vue'
import { useI18n } from 'vue-i18n'
import type { UserCompanyMembership } from '../types/company.types'

defineProps<{
  company: UserCompanyMembership
  canDelete: boolean
}>()

defineEmits<{
  open: []
  setDefault: []
  delete: []
}>()

const { t } = useI18n()
</script>

<template>
  <GlassCard class="company-card group cursor-pointer" @click="$emit('open')">
    <div class="mb-3 flex items-start gap-3">
      <div
        v-if="company.logo"
        class="flex h-11 w-11 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-[color:var(--color-surface-sunken)]"
      >
        <img :src="company.logo" :alt="company.name" class="h-full w-full object-contain" />
      </div>
      <div
        v-else
        class="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-[color:var(--color-accent-soft)] text-[color:var(--color-accent)]"
      >
        <i class="pi pi-building text-lg"></i>
      </div>
      <div class="min-w-0 flex-1">
        <h3 class="truncate text-base font-semibold text-[color:var(--color-text-primary)]">
          {{ company.name }}
        </h3>
        <p
          v-if="company.customIndustry || company.country"
          class="truncate text-xs text-[color:var(--color-text-muted)]"
        >
          {{ [company.customIndustry, company.country].filter(Boolean).join(' · ') }}
        </p>
      </div>
    </div>

    <p v-if="company.website" class="mb-2 truncate text-sm text-[color:var(--color-accent)]">
      <i class="pi pi-globe mr-1 text-xs"></i>{{ company.website }}
    </p>

    <div
      class="mt-3 flex items-center justify-between border-t border-[color:var(--color-border-soft)] pt-3"
    >
      <Tag
        v-if="company.isDefault"
        :value="t('companies.default')"
        severity="success"
        icon="pi pi-check"
      />
      <Button
        v-else
        :label="t('companies.setAsDefault')"
        icon="pi pi-star"
        text
        size="small"
        @click.stop="$emit('setDefault')"
      />
      <Button
        icon="pi pi-trash"
        severity="danger"
        text
        size="small"
        :disabled="!canDelete"
        :title="canDelete ? '' : t('companies.cannotDeleteLast')"
        class="opacity-0 transition-opacity group-hover:opacity-100"
        @click.stop="$emit('delete')"
      />
    </div>
  </GlassCard>
</template>

<style scoped>
.company-card {
  transition:
    transform 240ms var(--ease-ios),
    box-shadow 240ms var(--ease-ios);
}
.company-card:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-glass-float);
}
@media (prefers-reduced-motion: reduce) {
  .company-card {
    transition: box-shadow 180ms linear;
  }
  .company-card:hover {
    transform: none;
  }
}
</style>
