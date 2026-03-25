<script setup lang="ts">
import { onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import Tabs from 'primevue/tabs'
import TabList from 'primevue/tablist'
import Tab from 'primevue/tab'
import TabPanels from 'primevue/tabpanels'
import TabPanel from 'primevue/tabpanel'
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

const { t } = useI18n()
const store = useCvBuilderStore()

onMounted(async () => {
  await store.fetchProfile()
})
</script>

<template>
  <div class="mx-auto max-w-4xl">
    <h1 class="mb-6 text-2xl font-bold text-gray-900">
      {{ t('cvBuilder.title') }}
    </h1>

    <div
      v-if="store.loading && !store.profile"
      class="py-12 text-center text-gray-500"
    >
      {{ t('common.loading') }}
    </div>

    <template v-else-if="store.profile">
      <!-- CV Upload Parser -->
      <CvUploadParser class="mb-6" />

      <ProfileCompleteness
        :completeness="store.profile.completeness"
        class="mb-6"
      />

      <div class="rounded-lg bg-white shadow-sm">
        <Tabs value="0">
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
                <PersonalInfoForm />
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

      <!-- CV Template Selector / PDF Generation -->
      <CvTemplateSelector class="mt-6" />
    </template>

    <div v-else-if="store.error" class="py-12 text-center text-red-500">
      {{ store.error }}
    </div>
  </div>
</template>
