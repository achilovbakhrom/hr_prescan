<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import Tabs from 'primevue/tabs'
import TabList from 'primevue/tablist'
import Tab from 'primevue/tab'
import TabPanels from 'primevue/tabpanels'
import TabPanel from 'primevue/tabpanel'
import Button from 'primevue/button'
import Message from 'primevue/message'
import ProfileCompleteness from '../components/ProfileCompleteness.vue'
import PersonalInfoForm from '../components/PersonalInfoForm.vue'
import WorkExperienceForm from '../components/WorkExperienceForm.vue'
import EducationForm from '../components/EducationForm.vue'
import SkillsForm from '../components/SkillsForm.vue'
import LanguagesForm from '../components/LanguagesForm.vue'
import CertificationsForm from '../components/CertificationsForm.vue'
import CvUploadParser from '../components/CvUploadParser.vue'
import CvTemplateSelector from '../components/CvTemplateSelector.vue'
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
</script>

<template>
  <div class="mx-auto max-w-5xl">
    <div class="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <h1 class="text-2xl font-bold text-gray-900">
        {{ t('cvBuilder.title') }}
      </h1>
      <div v-if="store.profile" class="flex flex-wrap items-center gap-2">
        <CvUploadParser />
        <Button
          :label="t('cvBuilder.askAssistant')"
          icon="pi pi-sparkles"
          severity="secondary"
          size="small"
          @click="aiAssistant.open()"
        />
        <span class="hidden h-6 w-px bg-gray-200 sm:inline-block"></span>
        <CvTemplateSelector />
        <Button
          :label="t('common.save')"
          icon="pi pi-check"
          size="small"
          :loading="store.saving"
          @click="handleSave"
        />
      </div>
    </div>

    <div v-if="store.loading && !store.profile" class="py-12 text-center text-gray-500">
      {{ t('common.loading') }}
    </div>

    <template v-else-if="store.profile">
      <ProfileCompleteness :completeness="store.profile.completeness" class="mb-6" />

      <!-- Global store error (non-field) -->
      <Message
        v-if="store.error && Object.keys(store.fieldErrors).length === 0"
        severity="error"
        class="mb-4"
      >
        {{ store.error }}
      </Message>

      <div class="rounded-lg bg-white shadow-sm">
        <Tabs :value="activeTab" @update:value="(v: string | number) => (activeTab = String(v))">
          <TabList>
            <Tab value="0">
              <span class="hidden sm:inline">{{ t('cvBuilder.tabs.personal') }}</span>
              <span class="sm:hidden"><i class="pi pi-user"></i></span>
            </Tab>
            <Tab value="1">
              <span class="hidden sm:inline">{{ t('cvBuilder.tabs.experience') }}</span>
              <span class="sm:hidden"><i class="pi pi-briefcase"></i></span>
            </Tab>
            <Tab value="2">
              <span class="hidden sm:inline">{{ t('cvBuilder.tabs.education') }}</span>
              <span class="sm:hidden"><i class="pi pi-graduation-cap"></i></span>
            </Tab>
            <Tab value="3">
              <span class="hidden sm:inline">{{ t('cvBuilder.tabs.skills') }}</span>
              <span class="sm:hidden"><i class="pi pi-star"></i></span>
            </Tab>
            <Tab value="4">
              <span class="hidden sm:inline">{{ t('cvBuilder.tabs.languages') }}</span>
              <span class="sm:hidden"><i class="pi pi-globe"></i></span>
            </Tab>
            <Tab value="5">
              <span class="hidden sm:inline">{{ t('cvBuilder.tabs.certifications') }}</span>
              <span class="sm:hidden"><i class="pi pi-verified"></i></span>
            </Tab>
          </TabList>
          <TabPanels>
            <TabPanel value="0">
              <div class="p-4 sm:p-6">
                <PersonalInfoForm ref="personalFormRef" @switch-tab="switchToTab" />
              </div>
            </TabPanel>
            <TabPanel value="1">
              <div class="p-4 sm:p-6">
                <WorkExperienceForm />
              </div>
            </TabPanel>
            <TabPanel value="2">
              <div class="p-4 sm:p-6">
                <EducationForm />
              </div>
            </TabPanel>
            <TabPanel value="3">
              <div class="p-4 sm:p-6">
                <SkillsForm />
              </div>
            </TabPanel>
            <TabPanel value="4">
              <div class="p-4 sm:p-6">
                <LanguagesForm />
              </div>
            </TabPanel>
            <TabPanel value="5">
              <div class="p-4 sm:p-6">
                <CertificationsForm />
              </div>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </div>
    </template>

    <div v-else-if="store.error" class="py-12 text-center text-red-500">
      {{ store.error }}
    </div>
  </div>
</template>
