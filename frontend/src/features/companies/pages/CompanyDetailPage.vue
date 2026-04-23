<script setup lang="ts">
/**
 * CompanyDetailPage — company header + tabs (Info / Members / Vacancies).
 * Current backend only supports Info editing; Members/Vacancies placeholders
 * show but do not hit APIs that don't exist. Spec §9 Companies block.
 */
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import GlassCard from '@/shared/components/GlassCard.vue'
import CompanyDetailHeader from '../components/CompanyDetailHeader.vue'
import CompanyInfoView from '../components/CompanyInfoView.vue'
import CompanyInfoEditForm from '../components/CompanyInfoEditForm.vue'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { useCompanyStore } from '../stores/company.store'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const companyStore = useCompanyStore()
const activeTab = ref(0)
const editing = ref(false)
const saving = ref(false)

onMounted(() => {
  activeTab.value = 0
  companyStore.fetchCompanyDetail(route.params.id as string)
})

async function handleSave(payload: {
  name: string
  customIndustry: string
  website: string
  description: string
}): Promise<void> {
  saving.value = true
  try {
    await companyStore.updateCompany(route.params.id as string, payload)
    editing.value = false
  } catch {
    /* error surfaced via store */
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="mx-auto max-w-3xl space-y-4">
    <button
      class="flex items-center gap-1.5 text-sm text-[color:var(--color-text-muted)] transition-colors hover:text-[color:var(--color-text-primary)]"
      @click="router.push({ name: ROUTE_NAMES.COMPANY_LIST })"
    >
      <i class="pi pi-arrow-left text-xs"></i>
      {{ t('common.back') }}
    </button>

    <div v-if="companyStore.loading && !companyStore.currentCompany" class="py-12 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <GlassCard v-else-if="companyStore.error && !companyStore.currentCompany" class="text-center">
      <i class="pi pi-exclamation-circle mb-3 text-4xl text-[color:var(--color-danger)]"></i>
      <p class="text-[color:var(--color-danger)]">{{ companyStore.error }}</p>
    </GlassCard>

    <template v-else-if="companyStore.currentCompany">
      <CompanyDetailHeader
        :company="companyStore.currentCompany"
        :editing="editing"
        @edit="editing = true"
      />

      <p
        v-if="companyStore.error"
        class="rounded-lg border border-[color:var(--color-danger)] bg-[color:var(--color-danger)]/10 p-3 text-sm text-[color:var(--color-danger)]"
      >
        {{ companyStore.error }}
      </p>

      <TabView v-model:activeIndex="activeTab">
        <TabPanel value="0" :header="t('common.info', 'Info')">
          <div class="py-3">
            <GlassCard>
              <CompanyInfoView v-if="!editing" :company="companyStore.currentCompany" />
              <CompanyInfoEditForm
                v-else
                :company="companyStore.currentCompany"
                :saving="saving"
                @save="handleSave"
                @cancel="editing = false"
              />
            </GlassCard>
          </div>
        </TabPanel>
        <TabPanel value="1" :header="t('settings.team.title', 'Members')">
          <div class="py-3">
            <GlassCard>
              <p class="text-sm text-[color:var(--color-text-muted)]">
                {{ t('settings.team.manageHint', 'Manage team members in Settings → Team.') }}
              </p>
            </GlassCard>
          </div>
        </TabPanel>
        <TabPanel value="2" :header="t('nav.vacancies')">
          <div class="py-3">
            <GlassCard>
              <p class="text-sm text-[color:var(--color-text-muted)]">
                {{
                  t(
                    'vacancies.companyVacanciesHint',
                    'Vacancies scoped to this company appear on the main Vacancies list when it is active.',
                  )
                }}
              </p>
            </GlassCard>
          </div>
        </TabPanel>
      </TabView>
    </template>
  </div>
</template>
