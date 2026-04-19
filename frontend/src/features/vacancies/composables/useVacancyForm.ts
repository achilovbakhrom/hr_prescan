import { computed, nextTick, onMounted, ref, watch } from 'vue'
import type { FieldErrors } from '@/shared/api/errors'
import { getLocale } from '@/shared/i18n'
import { companyService } from '@/features/companies/services/company.service'
import type { UserCompanyMembership } from '@/features/companies/types/company.types'
import type {
  CreateVacancyRequest,
  EmploymentType,
  ExperienceLevel,
  InterviewMode,
  VacancyVisibility,
} from '../types/vacancy.types'

export function useVacancyForm(
  initialData: () => Partial<CreateVacancyRequest> | undefined,
  fieldErrors: () => FieldErrors | undefined,
) {
  const title = ref(initialData()?.title ?? '')
  const description = ref(initialData()?.description ?? '')
  const requirements = ref(initialData()?.requirements ?? '')
  const responsibilities = ref(initialData()?.responsibilities ?? '')
  const skills = ref<string[]>(initialData()?.skills ?? [])
  const salaryMin = ref<number | null>(initialData()?.salaryMin ?? null)
  const salaryMax = ref<number | null>(initialData()?.salaryMax ?? null)
  const salaryCurrency = ref(initialData()?.salaryCurrency ?? 'USD')
  const location = ref(initialData()?.location ?? '')
  const isRemote = ref(initialData()?.isRemote ?? false)
  const employmentType = ref<EmploymentType>(initialData()?.employmentType ?? 'full_time')
  const experienceLevel = ref<ExperienceLevel>(initialData()?.experienceLevel ?? 'middle')
  const deadline = ref<Date | null>(
    initialData()?.deadline ? new Date(initialData()!.deadline!) : null,
  )
  const visibility = ref<VacancyVisibility>(initialData()?.visibility ?? 'public')
  const cvRequired = ref(initialData()?.cvRequired ?? false)
  const prescanningPrompt = ref(initialData()?.prescanningPrompt ?? '')
  const prescanningLanguage = ref(initialData()?.prescanningLanguage ?? getLocale())
  const interviewEnabled = ref(initialData()?.interviewEnabled ?? false)
  const interviewMode = ref<InterviewMode>(initialData()?.interviewMode ?? 'chat')
  const interviewDuration = ref(initialData()?.interviewDuration ?? 30)
  const interviewPrompt = ref(initialData()?.interviewPrompt ?? '')
  const companyInfo = ref(initialData()?.companyInfo ?? '')
  const companyId = ref<string | null>(initialData()?.companyId ?? null)
  const companiesList = ref<UserCompanyMembership[]>([])
  const loadingCompanies = ref(false)
  const activeTab = ref(0)

  const selectedCompany = computed(
    () => companiesList.value.find((c) => c.id === companyId.value) ?? null,
  )

  const errors = computed<FieldErrors>(() => fieldErrors() ?? {})

  function hasError(field: string): boolean {
    return field in errors.value
  }

  function fieldError(field: string): string {
    return errors.value[field] ?? ''
  }

  const FIELD_TAB_MAP: Record<string, number> = {
    title: 0,
    description: 0,
    requirements: 0,
    responsibilities: 0,
    skills: 0,
    salaryMin: 0,
    salaryMax: 0,
    salaryCurrency: 0,
    location: 0,
    isRemote: 0,
    employmentType: 0,
    experienceLevel: 0,
    deadline: 0,
    companyId: 1,
    companyInfo: 1,
    prescanningPrompt: 2,
    interviewEnabled: 3,
    interviewMode: 3,
    interviewDuration: 3,
    interviewPrompt: 3,
    visibility: 4,
    cvRequired: 4,
  }

  watch(errors, (errs) => {
    if (!errs || Object.keys(errs).length === 0) return
    const firstField = Object.keys(errs)[0]
    const tabIndex = FIELD_TAB_MAP[firstField]
    if (tabIndex !== undefined) {
      activeTab.value = tabIndex
    }
    nextTick(() => {
      const firstInvalid = document.querySelector('.p-invalid, [data-field-error="true"]')
      if (firstInvalid) {
        firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    })
  })

  onMounted(async () => {
    loadingCompanies.value = true
    try {
      companiesList.value = await companyService.list()
      // Pre-select the user's default company if the form wasn't seeded with one.
      if (!companyId.value) {
        const def = companiesList.value.find((c) => c.isDefault)
        if (def) companyId.value = def.id
      }
    } catch {
      // silent; loading state ends in finally
    } finally {
      loadingCompanies.value = false
    }
  })

  const canSave = ref(true)
  watch([title, description], () => {
    canSave.value = Boolean(title.value && description.value)
  })

  function syncFromInitialData(d: Partial<CreateVacancyRequest>): void {
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
    prescanningLanguage.value = d.prescanningLanguage ?? 'en'
    interviewEnabled.value = d.interviewEnabled ?? false
    interviewMode.value = d.interviewMode ?? 'chat'
    interviewDuration.value = d.interviewDuration ?? 30
    interviewPrompt.value = d.interviewPrompt ?? ''
    companyInfo.value = d.companyInfo ?? ''
    companyId.value = d.companyId ?? null
  }

  function buildPayload(): CreateVacancyRequest {
    return {
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
      prescanningLanguage: prescanningLanguage.value,
      interviewEnabled: interviewEnabled.value,
      interviewMode: interviewMode.value,
      interviewDuration: interviewDuration.value,
      interviewPrompt: interviewPrompt.value || undefined,
      companyInfo: companyInfo.value || undefined,
      companyId: companyId.value || undefined,
    }
  }

  return {
    title,
    description,
    requirements,
    responsibilities,
    skills,
    salaryMin,
    salaryMax,
    salaryCurrency,
    location,
    isRemote,
    employmentType,
    experienceLevel,
    deadline,
    visibility,
    cvRequired,
    prescanningPrompt,
    prescanningLanguage,
    interviewEnabled,
    interviewMode,
    interviewDuration,
    interviewPrompt,
    companyInfo,
    companyId,
    companiesList,
    loadingCompanies,
    selectedCompany,
    activeTab,
    canSave,
    hasError,
    fieldError,
    syncFromInitialData,
    buildPayload,
  }
}
