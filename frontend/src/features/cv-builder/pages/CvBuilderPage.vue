<script setup lang="ts">
/**
 * CvBuilderPage — 3-column layout.
 * Left:   CvBuilderSectionNav (glass, section list + completeness dots)
 * Center: GlassCard containing form section for the active tab
 * Right:  CvBuilderPreview (solid paper-look, desktop only)
 * Mobile: stacks vertically with glass pill nav on top.
 * Spec: docs/design/spec.md §9.
 */
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Message from 'primevue/message'
import GlassCard from '@/shared/components/GlassCard.vue'
import ProfileCompleteness from '../components/ProfileCompleteness.vue'
import PersonalInfoForm from '../components/PersonalInfoForm.vue'
import WorkExperienceForm from '../components/WorkExperienceForm.vue'
import EducationForm from '../components/EducationForm.vue'
import SkillsForm from '../components/SkillsForm.vue'
import LanguagesForm from '../components/LanguagesForm.vue'
import CertificationsForm from '../components/CertificationsForm.vue'
import CvUploadParser from '../components/CvUploadParser.vue'
import CvTemplateSelector from '../components/CvTemplateSelector.vue'
import CvBuilderSectionNav from '../components/CvBuilderSectionNav.vue'
import CvBuilderPreview from '../components/CvBuilderPreview.vue'
import { useCvBuilderStore } from '../stores/cv-builder.store'
import { useAIAssistant } from '@/shared/composables/useAIAssistant'

const { t } = useI18n()
const store = useCvBuilderStore()
const aiAssistant = useAIAssistant()
const activeTab = ref('0')
const personalFormRef = ref<InstanceType<typeof PersonalInfoForm> | null>(null)

onMounted(async () => {
  await store.fetchProfile()
})

function switchToTab(tab: string): void {
  activeTab.value = tab
}

function handleSave(): void {
  if (activeTab.value === '0' && personalFormRef.value) {
    personalFormRef.value.save()
  }
}

const activeTitle = computed(() => {
  const map: Record<string, string> = {
    '0': t('cvBuilder.tabs.personal'),
    '1': t('cvBuilder.tabs.experience'),
    '2': t('cvBuilder.tabs.education'),
    '3': t('cvBuilder.tabs.skills'),
    '4': t('cvBuilder.tabs.languages'),
    '5': t('cvBuilder.tabs.certifications'),
  }
  return map[activeTab.value] || ''
})
</script>

<template>
  <div class="mx-auto max-w-[1400px]">
    <!-- Header -->
    <header class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-3xl font-semibold tracking-tight text-[color:var(--color-text-primary)]">
          {{ t('cvBuilder.title') }}
        </h1>
        <p class="mt-1 text-sm text-[color:var(--color-text-muted)]">
          {{ t('cvBuilder.subtitle') || 'Craft your CV section by section.' }}
        </p>
      </div>
      <div v-if="store.profile" class="flex flex-wrap items-center gap-2">
        <CvUploadParser />
        <Button
          :label="t('cvBuilder.askAssistant')"
          icon="pi pi-sparkles"
          severity="secondary"
          outlined
          size="small"
          @click="aiAssistant.open()"
        />
        <CvTemplateSelector />
        <Button
          :label="t('common.save')"
          icon="pi pi-check"
          size="small"
          :loading="store.saving"
          @click="handleSave"
        />
      </div>
    </header>

    <div v-if="store.loading && !store.profile" class="py-16 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <template v-else-if="store.profile">
      <ProfileCompleteness :completeness="store.profile.completeness" class="mb-6" />

      <Message
        v-if="store.error && Object.keys(store.fieldErrors).length === 0"
        severity="error"
        class="mb-4"
      >
        {{ store.error }}
      </Message>

      <!-- 3-column layout -->
      <div class="grid grid-cols-1 gap-6 lg:grid-cols-[240px_1fr] xl:grid-cols-[240px_1fr_360px]">
        <!-- Left rail (section nav) -->
        <CvBuilderSectionNav
          :active-id="activeTab"
          :completeness="store.profile.completeness"
          @select="switchToTab"
        />

        <!-- Center form -->
        <GlassCard class="min-w-0">
          <header class="mb-5 flex items-center gap-3">
            <h2 class="text-lg font-semibold text-[color:var(--color-text-primary)]">
              {{ activeTitle }}
            </h2>
          </header>
          <div class="min-w-0">
            <PersonalInfoForm
              v-show="activeTab === '0'"
              ref="personalFormRef"
              @switch-tab="switchToTab"
            />
            <WorkExperienceForm v-show="activeTab === '1'" />
            <EducationForm v-show="activeTab === '2'" />
            <SkillsForm v-show="activeTab === '3'" />
            <LanguagesForm v-show="activeTab === '4'" />
            <CertificationsForm v-show="activeTab === '5'" />
          </div>
        </GlassCard>

        <!-- Right preview (desktop-only XL) -->
        <CvBuilderPreview :profile="store.profile" />
      </div>
    </template>

    <div v-else-if="store.error" class="py-12 text-center text-[color:var(--color-danger)]">
      {{ store.error }}
    </div>
  </div>
</template>
