<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Dropdown from 'primevue/dropdown'
import InputNumber from 'primevue/inputnumber'
import Calendar from 'primevue/calendar'
import ToggleSwitch from 'primevue/toggleswitch'
import Chips from 'primevue/chips'
import Button from 'primevue/button'
import TabView from 'primevue/tabview'
import TabPanel from 'primevue/tabpanel'
import FileUpload from 'primevue/fileupload'
import { getEmploymentOptions, getExperienceOptions, CURRENCY_OPTIONS, getVisibilityOptions, getInterviewModeOptions } from '../constants/formOptions'
import { vacancyService } from '../services/vacancy.service'
import { extractErrorMessage } from '@/shared/api/errors'
import { employerService } from '@/features/employers/services/employer.service'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import type { EmployerCompany } from '@/features/employers/types/employer.types'
import type { CreateVacancyRequest, EmploymentType, ExperienceLevel, InterviewMode, VacancyVisibility } from '../types/vacancy.types'

const { t } = useI18n()
const router = useRouter()

const employmentOptions = computed(() => getEmploymentOptions(t))
const experienceOptions = computed(() => getExperienceOptions(t))
const visibilityOptions = computed(() => getVisibilityOptions(t))
const interviewModeOptions = computed(() => getInterviewModeOptions(t))

const props = defineProps<{ initialData?: Partial<CreateVacancyRequest>; loading?: boolean }>()
const emit = defineEmits<{ save: [data: CreateVacancyRequest] }>()

const activeTab = ref(0)

const title = ref(props.initialData?.title ?? '')
const description = ref(props.initialData?.description ?? '')
const requirements = ref(props.initialData?.requirements ?? '')
const responsibilities = ref(props.initialData?.responsibilities ?? '')
const skills = ref<string[]>(props.initialData?.skills ?? [])
const salaryMin = ref<number | null>(props.initialData?.salaryMin ?? null)
const salaryMax = ref<number | null>(props.initialData?.salaryMax ?? null)
const salaryCurrency = ref(props.initialData?.salaryCurrency ?? 'USD')
const location = ref(props.initialData?.location ?? '')
const isRemote = ref(props.initialData?.isRemote ?? false)
const employmentType = ref<EmploymentType>(props.initialData?.employmentType ?? 'full_time')
const experienceLevel = ref<ExperienceLevel>(props.initialData?.experienceLevel ?? 'middle')
const deadline = ref<Date | null>(props.initialData?.deadline ? new Date(props.initialData.deadline) : null)
const visibility = ref<VacancyVisibility>(props.initialData?.visibility ?? 'public')
const cvRequired = ref(props.initialData?.cvRequired ?? false)
const prescanningPrompt = ref(props.initialData?.prescanningPrompt ?? '')
const interviewEnabled = ref(props.initialData?.interviewEnabled ?? false)
const interviewMode = ref<InterviewMode>(props.initialData?.interviewMode ?? 'chat')
const interviewDuration = ref(props.initialData?.interviewDuration ?? 30)
const interviewPrompt = ref(props.initialData?.interviewPrompt ?? '')
const companyInfo = ref(props.initialData?.companyInfo ?? '')
const employerId = ref<string | null>(props.initialData?.employerId ?? null)
const employersList = ref<EmployerCompany[]>([])
const loadingEmployers = ref(false)

const selectedEmployer = computed(() =>
  employersList.value.find((e) => e.id === employerId.value) ?? null,
)

onMounted(async () => {
  loadingEmployers.value = true
  try {
    employersList.value = await employerService.list()
  } catch {
    // silent — dropdown will just be empty
  } finally {
    loadingEmployers.value = false
  }
})

const parsingFile = ref(false)
const parsingUrl = ref(false)
const parseError = ref('')
const websiteUrl = ref('')

async function handleFileUpload(event: { files: File[] }): void {
  const file = event.files?.[0]
  if (!file) return

  parsingFile.value = true
  parseError.value = ''
  try {
    companyInfo.value = await vacancyService.parseCompanyFile(file)
  } catch (err: unknown) {
    parseError.value = extractErrorMessage(err)
  } finally {
    parsingFile.value = false
  }
}

async function handleUrlParse(): Promise<void> {
  if (!websiteUrl.value) return

  parsingUrl.value = true
  parseError.value = ''
  try {
    companyInfo.value = await vacancyService.parseCompanyUrl(websiteUrl.value)
  } catch (err: unknown) {
    parseError.value = extractErrorMessage(err)
  } finally {
    parsingUrl.value = false
  }
}

const isParsing = ref(false)
watch([parsingFile, parsingUrl], () => {
  isParsing.value = parsingFile.value || parsingUrl.value
})

watch(() => props.initialData, (d) => {
  if (!d) return
  title.value = d.title ?? ''; description.value = d.description ?? ''
  requirements.value = d.requirements ?? ''; responsibilities.value = d.responsibilities ?? ''
  skills.value = d.skills ?? []; salaryMin.value = d.salaryMin ?? null
  salaryMax.value = d.salaryMax ?? null; salaryCurrency.value = d.salaryCurrency ?? 'USD'
  location.value = d.location ?? ''; isRemote.value = d.isRemote ?? false
  employmentType.value = d.employmentType ?? 'full_time'
  experienceLevel.value = d.experienceLevel ?? 'middle'
  deadline.value = d.deadline ? new Date(d.deadline) : null
  visibility.value = d.visibility ?? 'public'
  cvRequired.value = d.cvRequired ?? false
  prescanningPrompt.value = d.prescanningPrompt ?? ''
  interviewEnabled.value = d.interviewEnabled ?? false
  interviewMode.value = d.interviewMode ?? 'chat'
  interviewDuration.value = d.interviewDuration ?? 30
  interviewPrompt.value = d.interviewPrompt ?? ''
  companyInfo.value = d.companyInfo ?? ''
  employerId.value = d.employerId ?? null
})

const canSave = ref(true)
watch([title, description], () => {
  canSave.value = Boolean(title.value && description.value)
})

function handleSave(): void {
  emit('save', {
    title: title.value, description: description.value,
    requirements: requirements.value || undefined, responsibilities: responsibilities.value || undefined,
    skills: skills.value.length > 0 ? skills.value : undefined,
    salaryMin: salaryMin.value, salaryMax: salaryMax.value, salaryCurrency: salaryCurrency.value,
    location: location.value || undefined, isRemote: isRemote.value,
    employmentType: employmentType.value, experienceLevel: experienceLevel.value,
    deadline: deadline.value ? deadline.value.toISOString().split('T')[0] : null,
    visibility: visibility.value,
    cvRequired: cvRequired.value,
    prescanningPrompt: prescanningPrompt.value || undefined,
    interviewEnabled: interviewEnabled.value,
    interviewMode: interviewMode.value,
    interviewDuration: interviewDuration.value,
    interviewPrompt: interviewPrompt.value || undefined,
    companyInfo: companyInfo.value || undefined,
    employerId: employerId.value || undefined,
  })
}

</script>

<template>
  <form @submit.prevent="handleSave">
    <TabView v-model:activeIndex="activeTab">
      <!-- Tab 1: Basic Info (job details + location + salary) -->
      <TabPanel :header="t('vacancies.form.basicInfo')">
        <div class="space-y-4 py-2">

          <div>
            <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.title') }} <span class="text-red-500">*</span></label>
            <InputText v-model="title" class="w-full" :placeholder="t('vacancies.form.titlePlaceholder')" />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.description') }} <span class="text-red-500">*</span></label>
            <Textarea v-model="description" class="w-full" rows="5" :placeholder="t('vacancies.form.descriptionPlaceholder')" />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.requirements') }}</label>
            <Textarea v-model="requirements" class="w-full" rows="3" :placeholder="t('vacancies.form.requirementsPlaceholder')" />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.responsibilities') }}</label>
            <Textarea v-model="responsibilities" class="w-full" rows="3" :placeholder="t('vacancies.form.responsibilitiesPlaceholder')" />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.skills') }}</label>
            <Chips v-model="skills" class="w-full" :placeholder="t('vacancies.form.skillsPlaceholder')" />
          </div>

          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.location') }}</label>
              <InputText v-model="location" class="w-full" :placeholder="t('vacancies.form.locationPlaceholder')" />
            </div>
            <div class="flex items-end gap-3 pb-1">
              <label class="text-sm font-medium">{{ t('vacancies.form.remote') }}</label>
              <ToggleSwitch v-model="isRemote" />
            </div>
          </div>
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.employmentType') }}</label>
              <Dropdown v-model="employmentType" :options="employmentOptions" option-label="label" option-value="value" class="w-full" />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.experienceLevel') }}</label>
              <Dropdown v-model="experienceLevel" :options="experienceOptions" option-label="label" option-value="value" class="w-full" />
            </div>
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.deadline') }}</label>
            <Calendar v-model="deadline" class="w-full md:w-1/2" date-format="yy-mm-dd" :show-icon="true" />
          </div>

          <h4 class="pt-2 text-sm font-semibold text-gray-700">{{ t('vacancies.form.compensation') }}</h4>
          <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div>
              <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.salaryMin') }}</label>
              <InputNumber v-model="salaryMin" class="w-full" />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.salaryMax') }}</label>
              <InputNumber v-model="salaryMax" class="w-full" />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.currency') }}</label>
              <Dropdown v-model="salaryCurrency" :options="CURRENCY_OPTIONS" option-label="label" option-value="value" class="w-full" />
            </div>
          </div>

        </div>
      </TabPanel>

      <!-- Tab 2: Company Info -->
      <TabPanel :header="t('vacancies.form.companyInfo')">
        <div class="space-y-4 py-2">
          <div class="rounded-lg border border-blue-200 bg-blue-50/40 p-4">
            <div class="flex items-center gap-2">
              <i class="pi pi-building text-blue-600"></i>
              <span class="text-sm font-semibold text-blue-800">{{ t('vacancies.form.companyInfoLabel') }}</span>
            </div>
            <p class="mt-2 text-sm text-gray-600">
              {{ t('vacancies.form.companyInfoHint') }}
            </p>
          </div>

          <!-- Employer dropdown -->
          <div>
            <label class="mb-1 block text-sm font-medium">{{ t('employers.selectEmployer') }}</label>
            <div class="flex gap-2">
              <Dropdown
                v-model="employerId"
                :options="employersList"
                option-label="name"
                option-value="id"
                :placeholder="t('employers.selectEmployer')"
                :loading="loadingEmployers"
                show-clear
                class="flex-1"
              />
              <Button
                type="button"
                :label="t('employers.createNew')"
                icon="pi pi-plus"
                severity="secondary"
                size="small"
                @click="router.push({ name: ROUTE_NAMES.EMPLOYER_CREATE })"
              />
            </div>
          </div>

          <!-- Selected employer preview -->
          <div
            v-if="selectedEmployer"
            class="rounded-lg border border-gray-200 bg-gray-50 p-4"
          >
            <div class="mb-2 flex items-center gap-2">
              <div
                v-if="selectedEmployer.logo"
                class="flex h-8 w-8 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-white"
              >
                <img :src="selectedEmployer.logo" :alt="selectedEmployer.name" class="h-full w-full object-contain" />
              </div>
              <div v-else class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-blue-600">
                <i class="pi pi-building text-sm"></i>
              </div>
              <div>
                <p class="font-semibold text-gray-900">{{ selectedEmployer.name }}</p>
                <p v-if="selectedEmployer.industry" class="text-xs text-gray-500">{{ selectedEmployer.industry }}</p>
              </div>
            </div>
            <p v-if="selectedEmployer.description" class="whitespace-pre-line text-sm text-gray-600">
              {{ selectedEmployer.description }}
            </p>
          </div>

          <!-- Fallback: manual company info -->
          <div v-if="!employerId" class="border-t border-gray-100 pt-4">
            <p class="mb-3 text-sm text-gray-500">{{ t('employers.orCreateNew') }}</p>

            <!-- Option 1: Website URL -->
            <div>
              <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.fillFromWebsite') }}</label>
              <p class="mb-2 text-xs text-gray-400">{{ t('vacancies.form.websiteHint') }}</p>
              <div class="flex gap-2">
                <InputText v-model="websiteUrl" class="flex-1" :placeholder="t('vacancies.form.websitePlaceholder')" :disabled="isParsing" />
                <Button
                  type="button"
                  :label="t('vacancies.form.fetch')"
                  icon="pi pi-globe"
                  size="small"
                  :loading="parsingUrl"
                  :disabled="!websiteUrl || isParsing"
                  @click="handleUrlParse"
                />
              </div>
            </div>

            <!-- Option 2: File upload -->
            <div class="mt-4">
              <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.uploadDocument') }}</label>
              <p class="mb-2 text-xs text-gray-400">{{ t('vacancies.form.uploadHint') }}</p>
              <div class="flex items-center gap-3">
                <FileUpload
                  mode="basic"
                  accept=".pdf,.docx,.doc,.txt"
                  :max-file-size="10000000"
                  :choose-label="t('vacancies.form.uploadParse')"
                  :auto="true"
                  :custom-upload="true"
                  @uploader="handleFileUpload"
                  :disabled="isParsing"
                  class="text-sm"
                />
                <span v-if="parsingFile" class="flex items-center gap-2 text-sm text-gray-500">
                  <i class="pi pi-spinner pi-spin"></i> {{ t('vacancies.form.parsingFile') }}
                </span>
              </div>
            </div>

            <p v-if="parseError" class="mt-2 text-sm text-red-500">{{ parseError }}</p>

            <!-- Result textarea -->
            <div class="mt-4">
              <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.companyDescription') }}</label>
              <p class="mb-2 text-xs text-gray-400">{{ t('vacancies.form.companyDescriptionHint') }}</p>
              <Textarea v-model="companyInfo" class="w-full" rows="8" :placeholder="t('vacancies.form.companyInfoPlaceholder')" />
            </div>
          </div>

        </div>
      </TabPanel>

      <!-- Tab 3: Prescanning -->
      <TabPanel :header="t('vacancies.form.prescanning')">
        <div class="space-y-4 py-2">
          <div class="rounded-lg border border-teal-200 bg-teal-50/40 p-4">
            <div class="flex items-center gap-2">
              <i class="pi pi-comments text-teal-600"></i>
              <span class="text-sm font-semibold text-teal-800">{{ t('vacancies.form.prescanningAlwaysEnabled') }}</span>
            </div>
            <p class="mt-2 text-sm text-gray-600">
              {{ t('vacancies.form.prescanningHint') }}
            </p>
          </div>

          <div>
            <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.prescanningPrompt') }} ({{ t('common.optional') }})</label>
            <p class="mb-2 text-xs text-gray-400">{{ t('vacancies.form.prescanningPromptHint') }}</p>
            <Textarea v-model="prescanningPrompt" class="w-full" rows="5" :placeholder="t('vacancies.form.prescanningPromptPlaceholder')" />
          </div>

        </div>
      </TabPanel>

      <!-- Tab 4: Interview -->
      <TabPanel :header="t('vacancies.form.interview')">
        <div class="space-y-4 py-2">
          <div class="flex items-center justify-between rounded-lg border border-emerald-200 bg-emerald-50/40 p-4">
            <div>
              <div class="flex items-center gap-2">
                <i class="pi pi-video text-emerald-600"></i>
                <span class="text-sm font-semibold text-emerald-800">{{ t('vacancies.form.interviewOptional') }}</span>
              </div>
              <p class="mt-1 text-sm text-gray-600">
                {{ t('vacancies.form.interviewHint') }}
              </p>
            </div>
            <ToggleSwitch v-model="interviewEnabled" />
          </div>

          <div v-if="interviewEnabled" class="space-y-4">
            <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.interviewMode') }}</label>
                <Dropdown v-model="interviewMode" :options="interviewModeOptions" option-label="label" option-value="value" class="w-full" />
              </div>
              <div v-if="interviewMode === 'meet'">
                <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.interviewDuration') }}</label>
                <InputNumber v-model="interviewDuration" class="w-full" :min="10" :max="120" :step="5" />
              </div>
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.interviewPrompt') }} ({{ t('common.optional') }})</label>
              <p class="mb-2 text-xs text-gray-400">{{ t('vacancies.form.interviewPromptHint') }}</p>
              <Textarea v-model="interviewPrompt" class="w-full" rows="5" :placeholder="t('vacancies.form.interviewPromptPlaceholder')" />
            </div>
          </div>

        </div>
      </TabPanel>

      <!-- Tab 5: Settings -->
      <TabPanel :header="t('vacancies.form.settings')">
        <div class="space-y-5 py-2">
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.visibility') }}</label>
              <Dropdown v-model="visibility" :options="visibilityOptions" option-label="label" option-value="value" class="w-full" />
              <p class="mt-1 text-xs text-gray-400">{{ t('vacancies.form.visibilityPublicHint') }}</p>
            </div>
            <div class="flex items-start gap-3 pt-6">
              <ToggleSwitch v-model="cvRequired" />
              <div>
                <label class="text-sm font-medium">{{ t('vacancies.form.cvRequired') }}</label>
                <p class="text-xs text-gray-400">{{ t('vacancies.form.cvRequiredHint') }}</p>
              </div>
            </div>
          </div>

        </div>
      </TabPanel>
    </TabView>

    <!-- Save button — always visible below tabs -->
    <div class="mt-4 flex justify-end border-t border-gray-100 pt-4">
      <Button type="submit" :label="t('common.save')" icon="pi pi-check" :loading="loading" :disabled="!canSave" />
    </div>
  </form>
</template>
