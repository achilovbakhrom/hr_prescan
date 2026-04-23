<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import Dropdown from '@/shared/components/AppSelect.vue'
import ToggleSwitch from 'primevue/toggleswitch'
import GlassCard from '@/shared/components/GlassCard.vue'
import { getVisibilityOptions } from '../constants/formOptions'
import { useVacancyStore } from '../stores/vacancy.store'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { VacancyDetail, VacancyVisibility } from '../types/vacancy.types'

const props = defineProps<{
  vacancy: VacancyDetail
}>()

const { t } = useI18n()
const toast = useToast()
const confirm = useConfirm()
const router = useRouter()
const vacancyStore = useVacancyStore()

const visibilityOptions = computed(() => getVisibilityOptions(t))

const visibility = ref<VacancyVisibility>(props.vacancy.visibility)
const cvRequired = ref(props.vacancy.cvRequired)
const interviewEnabled = ref(props.vacancy.interviewEnabled)
const saving = ref(false)

watch(
  () => props.vacancy,
  (v) => {
    visibility.value = v.visibility
    cvRequired.value = v.cvRequired
    interviewEnabled.value = v.interviewEnabled
  },
  { deep: true },
)

const dirty = computed(
  () =>
    visibility.value !== props.vacancy.visibility ||
    cvRequired.value !== props.vacancy.cvRequired ||
    interviewEnabled.value !== props.vacancy.interviewEnabled,
)

async function save(): Promise<void> {
  saving.value = true
  try {
    await vacancyStore.updateVacancy(props.vacancy.id, {
      visibility: visibility.value,
      cvRequired: cvRequired.value,
      interviewEnabled: interviewEnabled.value,
    })
    toast.add({ severity: 'success', summary: t('common.saved'), life: 2500 })
  } catch {
    toast.add({ severity: 'error', summary: t('common.error'), life: 4000 })
  } finally {
    saving.value = false
  }
}

const canDelete = computed(
  () => props.vacancy.status === 'draft' || props.vacancy.status === 'archived',
)

/** Lock the interview-step toggle once active applications exist. */
const interviewLocked = computed(() => (props.vacancy.candidatesTotal ?? 0) > 0)

function confirmDelete(): void {
  confirm.require({
    message: t('vacancies.deleteConfirmMessage', { title: props.vacancy.title }),
    header: t('vacancies.deleteConfirmHeader'),
    icon: 'pi pi-trash',
    rejectLabel: t('common.cancel'),
    acceptLabel: t('common.delete'),
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await vacancyStore.deleteVacancy(props.vacancy.id)
        toast.add({ severity: 'success', summary: t('vacancies.deletedSuccess'), life: 3000 })
        router.push({ name: ROUTE_NAMES.VACANCY_LIST })
      } catch {
        toast.add({ severity: 'error', summary: t('common.error'), life: 4000 })
      }
    },
  })
}
</script>

<template>
  <div class="space-y-4">
    <!-- Visibility & CV -->
    <GlassCard :title="t('vacancies.settings.visibility')">
      <div class="grid grid-cols-1 gap-5 md:grid-cols-2">
        <div>
          <label class="mb-1 block text-xs font-medium text-[color:var(--color-text-secondary)]">{{
            t('vacancies.form.visibility')
          }}</label>
          <Dropdown
            v-model="visibility"
            :options="visibilityOptions"
            option-label="label"
            option-value="value"
            class="w-full"
          />
          <p class="mt-1 text-xs text-[color:var(--color-text-muted)]">
            {{ t('vacancies.form.visibilityPublicHint') }}
          </p>
        </div>
        <div class="flex items-start gap-3 pt-5">
          <ToggleSwitch v-model="cvRequired" />
          <div>
            <label class="text-sm font-medium text-[color:var(--color-text-primary)]">{{
              t('vacancies.form.cvRequired')
            }}</label>
            <p class="text-xs text-[color:var(--color-text-muted)]">
              {{ t('vacancies.form.cvRequiredHint') }}
            </p>
          </div>
        </div>
      </div>
    </GlassCard>

    <!-- Interview enable — locked once active applications exist -->
    <GlassCard :title="t('vacancies.settings.interviewStep')">
      <div class="flex items-start gap-3">
        <ToggleSwitch v-model="interviewEnabled" :disabled="interviewLocked" />
        <div>
          <label class="text-sm font-medium text-[color:var(--color-text-primary)]">{{
            t('vacancies.form.interviewOptional')
          }}</label>
          <p class="text-xs text-[color:var(--color-text-muted)]">
            {{ t('vacancies.form.interviewHint') }}
          </p>
          <p
            v-if="interviewLocked"
            class="mt-2 flex items-center gap-1 text-xs text-[color:var(--color-warning)]"
            :title="
              t(
                'vacancies.settings.interviewLockedTooltip',
                'Interview step cannot be changed once candidates have applied.',
              )
            "
          >
            <i class="pi pi-lock"></i>
            {{ t('vacancies.settings.interviewLocked', 'Locked — applications already received') }}
          </p>
        </div>
      </div>
    </GlassCard>

    <div v-if="dirty" class="flex justify-end">
      <Button :label="t('common.save')" icon="pi pi-check" :loading="saving" @click="save" />
    </div>

    <!-- Danger zone -->
    <GlassCard>
      <h3 class="mb-2 text-sm font-semibold text-[color:var(--color-danger)]">
        {{ t('vacancies.settings.dangerZone') }}
      </h3>
      <p class="mb-3 text-xs text-[color:var(--color-text-muted)]">
        {{ t('vacancies.settings.dangerZoneHint') }}
      </p>
      <Button
        :label="t('vacancies.settings.deleteVacancy')"
        icon="pi pi-trash"
        severity="danger"
        size="small"
        :disabled="!canDelete"
        @click="confirmDelete"
      />
      <p v-if="!canDelete" class="mt-2 text-xs text-[color:var(--color-text-muted)]">
        {{ t('vacancies.settings.deleteOnlyDraftArchived') }}
      </p>
    </GlassCard>
  </div>
</template>
