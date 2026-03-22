<script setup lang="ts">
import { ref, watch } from 'vue'
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
import { EMPLOYMENT_OPTIONS, EXPERIENCE_OPTIONS, CURRENCY_OPTIONS, VISIBILITY_OPTIONS } from '../constants/formOptions'
import { vacancyService } from '../services/vacancy.service'
import { extractErrorMessage } from '@/shared/api/errors'
import type { CreateVacancyRequest, EmploymentType, ExperienceLevel, InterviewMode, VacancyVisibility } from '../types/vacancy.types'

const INTERVIEW_MODE_OPTIONS = [
  { label: 'Chat', value: 'chat' },
  { label: 'Meet (Video)', value: 'meet' },
]

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
  })
}

</script>

<template>
  <form @submit.prevent="handleSave">
    <TabView v-model:activeIndex="activeTab">
      <!-- Tab 1: Basic Info (job details + location + salary) -->
      <TabPanel header="Basic Info">
        <div class="space-y-4 py-2">

          <div>
            <label class="mb-1 block text-sm font-medium">Title <span class="text-red-500">*</span></label>
            <InputText v-model="title" class="w-full" placeholder="e.g. Senior Frontend Developer" />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium">Description <span class="text-red-500">*</span></label>
            <Textarea v-model="description" class="w-full" rows="5" placeholder="Job description..." />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium">Requirements</label>
            <Textarea v-model="requirements" class="w-full" rows="3" placeholder="Requirements..." />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium">Responsibilities</label>
            <Textarea v-model="responsibilities" class="w-full" rows="3" placeholder="Responsibilities..." />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium">Skills</label>
            <Chips v-model="skills" class="w-full" placeholder="Add skill and press Enter" />
          </div>

          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label class="mb-1 block text-sm font-medium">Location</label>
              <InputText v-model="location" class="w-full" placeholder="e.g. New York, NY" />
            </div>
            <div class="flex items-end gap-3 pb-1">
              <label class="text-sm font-medium">Remote</label>
              <ToggleSwitch v-model="isRemote" />
            </div>
          </div>
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label class="mb-1 block text-sm font-medium">Employment Type</label>
              <Dropdown v-model="employmentType" :options="EMPLOYMENT_OPTIONS" option-label="label" option-value="value" class="w-full" />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium">Experience Level</label>
              <Dropdown v-model="experienceLevel" :options="EXPERIENCE_OPTIONS" option-label="label" option-value="value" class="w-full" />
            </div>
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium">Deadline</label>
            <Calendar v-model="deadline" class="w-full md:w-1/2" date-format="yy-mm-dd" :show-icon="true" />
          </div>

          <h4 class="pt-2 text-sm font-semibold text-gray-700">Compensation</h4>
          <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div>
              <label class="mb-1 block text-sm font-medium">Min Salary</label>
              <InputNumber v-model="salaryMin" class="w-full" />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium">Max Salary</label>
              <InputNumber v-model="salaryMax" class="w-full" />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium">Currency</label>
              <Dropdown v-model="salaryCurrency" :options="CURRENCY_OPTIONS" option-label="label" option-value="value" class="w-full" />
            </div>
          </div>

        </div>
      </TabPanel>

      <!-- Tab 2: Company Info -->
      <TabPanel header="Company Info">
        <div class="space-y-4 py-2">
          <div class="rounded-lg border border-blue-200 bg-blue-50/40 p-4">
            <div class="flex items-center gap-2">
              <i class="pi pi-building text-blue-600"></i>
              <span class="text-sm font-semibold text-blue-800">Company Information for AI</span>
            </div>
            <p class="mt-2 text-sm text-gray-600">
              The AI interviewer will use this to introduce the company to candidates. You can fill it from a website, upload a document, or type it manually.
            </p>
          </div>

          <!-- Option 1: Website URL -->
          <div>
            <label class="mb-1 block text-sm font-medium">Fill from website</label>
            <p class="mb-2 text-xs text-gray-400">Enter your company's About page or website URL and AI will extract the info.</p>
            <div class="flex gap-2">
              <InputText v-model="websiteUrl" class="flex-1" placeholder="https://yourcompany.com/about" :disabled="isParsing" />
              <Button
                type="button"
                label="Fetch"
                icon="pi pi-globe"
                size="small"
                :loading="parsingUrl"
                :disabled="!websiteUrl || isParsing"
                @click="handleUrlParse"
              />
            </div>
          </div>

          <!-- Option 2: File upload -->
          <div>
            <label class="mb-1 block text-sm font-medium">Or upload a document</label>
            <p class="mb-2 text-xs text-gray-400">PDF, DOCX, or TXT (e.g. company brochure, pitch deck). Max 10MB.</p>
            <div class="flex items-center gap-3">
              <FileUpload
                mode="basic"
                accept=".pdf,.docx,.doc,.txt"
                :max-file-size="10000000"
                choose-label="Upload & Parse"
                :auto="true"
                :custom-upload="true"
                @uploader="handleFileUpload"
                :disabled="isParsing"
                class="text-sm"
              />
              <span v-if="parsingFile" class="flex items-center gap-2 text-sm text-gray-500">
                <i class="pi pi-spinner pi-spin"></i> Parsing file...
              </span>
            </div>
          </div>

          <p v-if="parseError" class="text-sm text-red-500">{{ parseError }}</p>

          <!-- Result textarea -->
          <div>
            <label class="mb-1 block text-sm font-medium">Company Description</label>
            <p class="mb-2 text-xs text-gray-400">Edit or write the company introduction below. You can adjust any AI-generated text.</p>
            <Textarea v-model="companyInfo" class="w-full" rows="8" placeholder="e.g. We are a leading fintech company based in Tashkent, building next-gen payment solutions. Our team of 50+ engineers works on..." />
          </div>

        </div>
      </TabPanel>

      <!-- Tab 3: Prescanning -->
      <TabPanel header="Prescanning">
        <div class="space-y-4 py-2">
          <div class="rounded-lg border border-teal-200 bg-teal-50/40 p-4">
            <div class="flex items-center gap-2">
              <i class="pi pi-comments text-teal-600"></i>
              <span class="text-sm font-semibold text-teal-800">Always enabled</span>
            </div>
            <p class="mt-2 text-sm text-gray-600">
              Every candidate goes through an automated AI prescanning chat after applying. The AI asks screening questions based on the vacancy details.
            </p>
          </div>

          <div>
            <label class="mb-1 block text-sm font-medium">Additional Instructions for AI (optional)</label>
            <p class="mb-2 text-xs text-gray-400">Guide the AI's behavior during prescanning. It already knows the vacancy details.</p>
            <Textarea v-model="prescanningPrompt" class="w-full" rows="5" placeholder="e.g. Focus on their experience with microservices architecture. Be lenient with junior candidates. Ask about their availability timeline." />
          </div>

        </div>
      </TabPanel>

      <!-- Tab 4: Interview -->
      <TabPanel header="Interview">
        <div class="space-y-4 py-2">
          <div class="flex items-center justify-between rounded-lg border border-emerald-200 bg-emerald-50/40 p-4">
            <div>
              <div class="flex items-center gap-2">
                <i class="pi pi-video text-emerald-600"></i>
                <span class="text-sm font-semibold text-emerald-800">Second-step AI Interview</span>
              </div>
              <p class="mt-1 text-sm text-gray-600">
                Enable a deeper interview for candidates who passed prescanning.
              </p>
            </div>
            <ToggleSwitch v-model="interviewEnabled" />
          </div>

          <div v-if="interviewEnabled" class="space-y-4">
            <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div>
                <label class="mb-1 block text-sm font-medium">Interview Mode</label>
                <Dropdown v-model="interviewMode" :options="INTERVIEW_MODE_OPTIONS" option-label="label" option-value="value" class="w-full" />
              </div>
              <div v-if="interviewMode === 'meet'">
                <label class="mb-1 block text-sm font-medium">Duration (minutes)</label>
                <InputNumber v-model="interviewDuration" class="w-full" :min="10" :max="120" :step="5" />
              </div>
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium">Additional Instructions for AI (optional)</label>
              <p class="mb-2 text-xs text-gray-400">Guide the interview AI. It will be tougher and more probing than prescanning.</p>
              <Textarea v-model="interviewPrompt" class="w-full" rows="5" placeholder="e.g. Ask deeper technical questions about system design. Present a real-world scenario. Be strict about technical knowledge." />
            </div>
          </div>

        </div>
      </TabPanel>

      <!-- Tab 5: Settings -->
      <TabPanel header="Settings">
        <div class="space-y-5 py-2">
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <div>
              <label class="mb-1 block text-sm font-medium">Visibility</label>
              <Dropdown v-model="visibility" :options="VISIBILITY_OPTIONS" option-label="label" option-value="value" class="w-full" />
              <p class="mt-1 text-xs text-gray-400">Public vacancies appear on the job board. Private ones are link-only.</p>
            </div>
            <div class="flex items-start gap-3 pt-6">
              <ToggleSwitch v-model="cvRequired" />
              <div>
                <label class="text-sm font-medium">CV Required</label>
                <p class="text-xs text-gray-400">Require candidates to upload a CV when applying</p>
              </div>
            </div>
          </div>

        </div>
      </TabPanel>
    </TabView>

    <!-- Save button — always visible below tabs -->
    <div class="mt-4 flex justify-end border-t border-gray-100 pt-4">
      <Button type="submit" label="Save" icon="pi pi-check" :loading="loading" :disabled="!canSave" />
    </div>
  </form>
</template>
