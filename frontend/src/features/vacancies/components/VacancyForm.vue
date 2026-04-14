<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
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
import Dialog from 'primevue/dialog'
import SelectButton from 'primevue/selectbutton'
import {
  getEmploymentOptions,
  getExperienceOptions,
  CURRENCY_OPTIONS,
  getVisibilityOptions,
  getInterviewModeOptions,
} from '../constants/formOptions'
import { extractErrorMessage } from '@/shared/api/errors'
import { employerService } from '@/features/employers/services/employer.service'
import type { EmployerCompany } from '@/features/employers/types/employer.types'
import type {
  CreateVacancyRequest,
  EmploymentType,
  ExperienceLevel,
  InterviewMode,
  VacancyVisibility,
} from '../types/vacancy.types'

const props = defineProps<{ initialData?: Partial<CreateVacancyRequest>; loading?: boolean }>()

const emit = defineEmits<{ save: [data: CreateVacancyRequest] }>()

const { t } = useI18n()

const employmentOptions = computed(() => getEmploymentOptions(t))
const experienceOptions = computed(() => getExperienceOptions(t))
const visibilityOptions = computed(() => getVisibilityOptions(t))
const interviewModeOptions = computed(() => getInterviewModeOptions(t))

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
const deadline = ref<Date | null>(
  props.initialData?.deadline ? new Date(props.initialData.deadline) : null,
)
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

const selectedEmployer = computed(
  () => employersList.value.find((e) => e.id === employerId.value) ?? null,
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

// --- Create Employer Dialog ---
const showCreateDialog = ref(false)
const createMode = ref<'manual' | 'file' | 'website'>('manual')
const createModeOptions = computed(() => [
  { label: t('employers.manual'), value: 'manual' },
  { label: t('employers.file'), value: 'file' },
  { label: t('employers.fromWebsite'), value: 'website' },
])
const newEmployerName = ref('')
const newEmployerIndustry = ref('')
const newEmployerWebsite = ref('')
const newEmployerDescription = ref('')
const newEmployerUrl = ref('')
const creatingEmployer = ref(false)
const createError = ref('')

function openCreateDialog(): void {
  newEmployerName.value = ''
  newEmployerIndustry.value = ''
  newEmployerWebsite.value = ''
  newEmployerDescription.value = ''
  newEmployerUrl.value = ''
  createMode.value = 'manual'
  createError.value = ''
  showCreateDialog.value = true
}

async function handleCreateEmployer(): Promise<void> {
  if (!newEmployerName.value) return
  creatingEmployer.value = true
  createError.value = ''
  try {
    let employer: EmployerCompany
    if (createMode.value === 'file') {
      // File mode handled separately via handleCreateFromFile
      return
    } else if (createMode.value === 'website') {
      employer = await employerService.createFromUrl(newEmployerName.value, newEmployerUrl.value)
    } else {
      employer = await employerService.create({
        name: newEmployerName.value,
        industry: newEmployerIndustry.value,
        website: newEmployerWebsite.value,
        description: newEmployerDescription.value,
      })
    }
    employersList.value.push(employer)
    employerId.value = employer.id
    showCreateDialog.value = false
  } catch (err: unknown) {
    createError.value = extractErrorMessage(err)
  } finally {
    creatingEmployer.value = false
  }
}

async function handleCreateFromFile(event: { files: File | File[] }): Promise<void> {
  const files = Array.isArray(event.files) ? event.files : [event.files]
  const file = files[0]
  if (!file || !newEmployerName.value) return
  creatingEmployer.value = true
  createError.value = ''
  try {
    const employer = await employerService.createFromFile(newEmployerName.value, file)
    employersList.value.push(employer)
    employerId.value = employer.id
    showCreateDialog.value = false
  } catch (err: unknown) {
    createError.value = extractErrorMessage(err)
  } finally {
    creatingEmployer.value = false
  }
}

watch(
  () => props.initialData,
  (d) => {
    if (!d) return
    title.value = d.title ?? ''
    description.value = d.description ?? ''
    requirements.value = d.requirements ?? ''
    responsibilities.value = d.responsibilities ?? ''
    skills.value = d.skills ?? []
    salaryMin.value = d.salaryMin ?? null
    salaryMax.value = d.salaryMax ?? null
    salaryCurrency.value = d.salaryCurrency ?? 'USD'
    location.value = d.location ?? ''
    isRemote.value = d.isRemote ?? false
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
  },
)

const canSave = ref(true)
watch([title, description], () => {
  canSave.value = Boolean(title.value && description.value)
})

function handleSave(): void {
  emit('save', {
    title: title.value,
    description: description.value,
    requirements: requirements.value || undefined,
    responsibilities: responsibilities.value || undefined,
    skills: skills.value.length > 0 ? skills.value : undefined,
    salaryMin: salaryMin.value,
    salaryMax: salaryMax.value,
    salaryCurrency: salaryCurrency.value,
    location: location.value || undefined,
    isRemote: isRemote.value,
    employmentType: employmentType.value,
    experienceLevel: experienceLevel.value,
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
      <TabPanel value="basicInfo" :header="t('vacancies.form.basicInfo')">
        <div class="space-y-4 py-2">
          <div>
            <label class="mb-1 block text-sm font-medium"
              >{{ t('vacancies.form.title') }} <span class="text-red-500">*</span></label
            >
            <InputText
              v-model="title"
              class="w-full"
              :placeholder="t('vacancies.form.titlePlaceholder')"
            />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium"
              >{{ t('vacancies.form.description') }} <span class="text-red-500">*</span></label
            >
            <Textarea
              v-model="description"
              class="w-full"
              rows="5"
              :placeholder="t('vacancies.form.descriptionPlaceholder')"
            />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium">{{
              t('vacancies.form.requirements')
            }}</label>
            <Textarea
              v-model="requirements"
              class="w-full"
              rows="3"
              :placeholder="t('vacancies.form.requirementsPlaceholder')"
            />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium">{{
              t('vacancies.form.responsibilities')
            }}</label>
            <Textarea
              v-model="responsibilities"
              class="w-full"
              rows="3"
              :placeholder="t('vacancies.form.responsibilitiesPlaceholder')"
            />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.skills') }}</label>
            <Chips
              v-model="skills"
              class="w-full"
              :placeholder="t('vacancies.form.skillsPlaceholder')"
            />
          </div>

          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label class="mb-1 block text-sm font-medium">{{
                t('vacancies.form.location')
              }}</label>
              <InputText
                v-model="location"
                class="w-full"
                :placeholder="t('vacancies.form.locationPlaceholder')"
              />
            </div>
            <div class="flex items-end gap-3 pb-1">
              <label class="text-sm font-medium">{{ t('vacancies.form.remote') }}</label>
              <ToggleSwitch v-model="isRemote" />
            </div>
          </div>
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label class="mb-1 block text-sm font-medium">{{
                t('vacancies.form.employmentType')
              }}</label>
              <Dropdown
                v-model="employmentType"
                :options="employmentOptions"
                option-label="label"
                option-value="value"
                class="w-full"
              />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium">{{
                t('vacancies.form.experienceLevel')
              }}</label>
              <Dropdown
                v-model="experienceLevel"
                :options="experienceOptions"
                option-label="label"
                option-value="value"
                class="w-full"
              />
            </div>
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium">{{ t('vacancies.form.deadline') }}</label>
            <Calendar
              v-model="deadline"
              class="w-full md:w-1/2"
              date-format="yy-mm-dd"
              :show-icon="true"
            />
          </div>

          <h4 class="pt-2 text-sm font-semibold text-gray-700">
            {{ t('vacancies.form.compensation') }}
          </h4>
          <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div>
              <label class="mb-1 block text-sm font-medium">{{
                t('vacancies.form.salaryMin')
              }}</label>
              <InputNumber v-model="salaryMin" class="w-full" />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium">{{
                t('vacancies.form.salaryMax')
              }}</label>
              <InputNumber v-model="salaryMax" class="w-full" />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium">{{
                t('vacancies.form.currency')
              }}</label>
              <Dropdown
                v-model="salaryCurrency"
                :options="CURRENCY_OPTIONS"
                option-label="label"
                option-value="value"
                class="w-full"
              />
            </div>
          </div>
        </div>
      </TabPanel>

      <!-- Tab 2: Company -->
      <TabPanel value="company" :header="t('vacancies.form.companyInfo')">
        <div class="space-y-4 py-2">
          <!-- Employer dropdown + Add New -->
          <div>
            <label class="mb-1 block text-sm font-medium">{{
              t('employers.selectEmployer')
            }}</label>
            <div class="flex gap-2">
              <Dropdown
                v-model="employerId"
                :options="employersList"
                option-label="name"
                option-value="id"
                :placeholder="t('employers.selectEmployer')"
                :loading="loadingEmployers"
                show-clear
                filter
                class="flex-1"
              />
              <Button
                type="button"
                icon="pi pi-plus"
                :label="t('employers.createNew')"
                severity="secondary"
                size="small"
                @click="openCreateDialog"
              />
            </div>
          </div>

          <!-- Selected employer preview -->
          <div v-if="selectedEmployer" class="rounded-xl border border-gray-200 bg-gray-50 p-4">
            <div class="flex items-center gap-3">
              <div
                v-if="selectedEmployer.logo"
                class="flex h-10 w-10 shrink-0 items-center justify-center overflow-hidden rounded-lg bg-white ring-1 ring-gray-200"
              >
                <img
                  :src="selectedEmployer.logo"
                  :alt="selectedEmployer.name"
                  class="h-full w-full object-contain"
                />
              </div>
              <div
                v-else
                class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-blue-50 text-blue-600"
              >
                <i class="pi pi-building"></i>
              </div>
              <div class="min-w-0 flex-1">
                <p class="font-semibold text-gray-900">{{ selectedEmployer.name }}</p>
                <p v-if="selectedEmployer.industry" class="text-xs text-gray-500">
                  {{ selectedEmployer.industry }}
                </p>
                <a
                  v-if="selectedEmployer.website"
                  :href="selectedEmployer.website"
                  target="_blank"
                  class="text-xs text-blue-500 hover:underline"
                  >{{ selectedEmployer.website }}</a
                >
              </div>
            </div>
            <p
              v-if="selectedEmployer.description"
              class="mt-3 whitespace-pre-line text-sm leading-relaxed text-gray-600"
            >
              {{
                selectedEmployer.description.length > 300
                  ? selectedEmployer.description.slice(0, 300) + '...'
                  : selectedEmployer.description
              }}
            </p>
          </div>

          <!-- Empty state -->
          <div v-else class="rounded-xl border border-dashed border-gray-200 py-10 text-center">
            <i class="pi pi-building mb-2 text-3xl text-gray-300"></i>
            <p class="text-sm text-gray-500">{{ t('employers.selectEmployer') }}</p>
            <p class="mt-1 text-xs text-gray-400">{{ t('employers.orCreateNew') }}</p>
          </div>
        </div>
      </TabPanel>

      <!-- Tab 3: Prescanning -->
      <TabPanel value="prescanning" :header="t('vacancies.form.prescanning')">
        <div class="space-y-4 py-2">
          <div class="rounded-lg border border-teal-200 bg-teal-50/40 p-4">
            <div class="flex items-center gap-2">
              <i class="pi pi-comments text-teal-600"></i>
              <span class="text-sm font-semibold text-teal-800">{{
                t('vacancies.form.prescanningAlwaysEnabled')
              }}</span>
            </div>
            <p class="mt-2 text-sm text-gray-600">
              {{ t('vacancies.form.prescanningHint') }}
            </p>
          </div>

          <div>
            <label class="mb-1 block text-sm font-medium"
              >{{ t('vacancies.form.prescanningPrompt') }} ({{ t('common.optional') }})</label
            >
            <p class="mb-2 text-xs text-gray-400">
              {{ t('vacancies.form.prescanningPromptHint') }}
            </p>
            <Textarea
              v-model="prescanningPrompt"
              class="w-full"
              rows="5"
              :placeholder="t('vacancies.form.prescanningPromptPlaceholder')"
            />
          </div>
        </div>
      </TabPanel>

      <!-- Tab 4: Interview -->
      <TabPanel value="interview" :header="t('vacancies.form.interview')">
        <div class="space-y-4 py-2">
          <div
            class="flex items-center justify-between rounded-lg border border-emerald-200 bg-emerald-50/40 p-4"
          >
            <div>
              <div class="flex items-center gap-2">
                <i class="pi pi-video text-emerald-600"></i>
                <span class="text-sm font-semibold text-emerald-800">{{
                  t('vacancies.form.interviewOptional')
                }}</span>
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
                <label class="mb-1 block text-sm font-medium">{{
                  t('vacancies.form.interviewMode')
                }}</label>
                <Dropdown
                  v-model="interviewMode"
                  :options="interviewModeOptions"
                  option-label="label"
                  option-value="value"
                  class="w-full"
                />
              </div>
              <div v-if="interviewMode === 'meet'">
                <label class="mb-1 block text-sm font-medium">{{
                  t('vacancies.form.interviewDuration')
                }}</label>
                <InputNumber
                  v-model="interviewDuration"
                  class="w-full"
                  :min="10"
                  :max="120"
                  :step="5"
                />
              </div>
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium"
                >{{ t('vacancies.form.interviewPrompt') }} ({{ t('common.optional') }})</label
              >
              <p class="mb-2 text-xs text-gray-400">
                {{ t('vacancies.form.interviewPromptHint') }}
              </p>
              <Textarea
                v-model="interviewPrompt"
                class="w-full"
                rows="5"
                :placeholder="t('vacancies.form.interviewPromptPlaceholder')"
              />
            </div>
          </div>
        </div>
      </TabPanel>

      <!-- Tab 5: Settings -->
      <TabPanel value="settings" :header="t('vacancies.form.settings')">
        <div class="space-y-5 py-2">
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label class="mb-1 block text-sm font-medium">{{
                t('vacancies.form.visibility')
              }}</label>
              <Dropdown
                v-model="visibility"
                :options="visibilityOptions"
                option-label="label"
                option-value="value"
                class="w-full"
              />
              <p class="mt-1 text-xs text-gray-400">
                {{ t('vacancies.form.visibilityPublicHint') }}
              </p>
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
      <Button
        type="submit"
        :label="t('common.save')"
        icon="pi pi-check"
        :loading="loading"
        :disabled="!canSave"
      />
    </div>
  </form>

  <!-- Create Employer Dialog (outside form to avoid TabView swallowing it) -->
  <Dialog
    v-model:visible="showCreateDialog"
    :header="t('employers.create')"
    modal
    :style="{ width: '500px' }"
    :breakpoints="{ '640px': '95vw' }"
  >
    <div class="space-y-4">
      <SelectButton
        v-model="createMode"
        :options="createModeOptions"
        option-label="label"
        option-value="value"
        class="w-full"
      />

      <div>
        <label class="mb-1 block text-sm font-medium"
          >{{ t('employers.name') }} <span class="text-red-500">*</span></label
        >
        <InputText
          v-model="newEmployerName"
          class="w-full"
          :placeholder="t('employers.namePlaceholder')"
        />
      </div>

      <template v-if="createMode === 'manual'">
        <div>
          <label class="mb-1 block text-sm font-medium">{{ t('employers.industry') }}</label>
          <InputText v-model="newEmployerIndustry" class="w-full" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">{{ t('employers.website') }}</label>
          <InputText v-model="newEmployerWebsite" class="w-full" placeholder="https://" />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium">{{ t('employers.description') }}</label>
          <Textarea v-model="newEmployerDescription" class="w-full" rows="4" />
        </div>
      </template>

      <template v-if="createMode === 'website'">
        <div>
          <label class="mb-1 block text-sm font-medium">{{ t('employers.websiteUrl') }}</label>
          <InputText
            v-model="newEmployerUrl"
            class="w-full"
            :placeholder="t('employers.urlPlaceholder')"
          />
          <p class="mt-1 text-xs text-gray-400">AI will extract company info from this page</p>
        </div>
      </template>

      <template v-if="createMode === 'file'">
        <div>
          <label class="mb-1 block text-sm font-medium">{{ t('employers.uploadFile') }}</label>
          <p class="mb-2 text-xs text-gray-400">PDF, DOCX, or TXT. AI will extract company info.</p>
          <FileUpload
            mode="basic"
            accept=".pdf,.docx,.doc,.txt"
            :max-file-size="10000000"
            :choose-label="t('employers.uploadFile')"
            :auto="true"
            :custom-upload="true"
            :disabled="creatingEmployer"
            @uploader="handleCreateFromFile"
          />
        </div>
      </template>

      <p v-if="createError" class="text-sm text-red-500">{{ createError }}</p>
    </div>

    <template #footer>
      <div class="flex justify-end gap-2">
        <Button
          :label="t('common.cancel')"
          severity="secondary"
          text
          @click="showCreateDialog = false"
        />
        <Button
          v-if="createMode !== 'file'"
          :label="t('common.save')"
          icon="pi pi-check"
          :loading="creatingEmployer"
          :disabled="!newEmployerName"
          @click="handleCreateEmployer"
        />
      </div>
    </template>
  </Dialog>
</template>
