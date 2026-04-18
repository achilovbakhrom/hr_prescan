<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import Dialog from 'primevue/dialog'
import InputText from 'primevue/inputtext'
import { ROUTE_NAMES } from '@/shared/constants/routes'
import { globalSearch, type SearchResults } from '@/shared/api/search'

const visible = defineModel<boolean>('visible', { required: true })

const { t } = useI18n()
const router = useRouter()

const query = ref('')
const loading = ref(false)
const results = ref<SearchResults>({ vacancies: [], candidates: [] })
const inputRef = ref<InstanceType<typeof InputText> | null>(null)

let searchTimeout: ReturnType<typeof setTimeout> | null = null

watch(visible, async (val) => {
  if (val) {
    query.value = ''
    results.value = { vacancies: [], candidates: [] }
    await nextTick()
    const el = (inputRef.value as unknown as { $el?: HTMLInputElement })?.$el
    if (el && 'focus' in el) (el as HTMLInputElement).focus()
  }
})

function onInput(): void {
  if (searchTimeout) clearTimeout(searchTimeout)
  const q = query.value.trim()
  if (!q) {
    results.value = { vacancies: [], candidates: [] }
    return
  }
  searchTimeout = setTimeout(async () => {
    loading.value = true
    try {
      results.value = await globalSearch(q)
    } catch {
      results.value = { vacancies: [], candidates: [] }
    } finally {
      loading.value = false
    }
  }, 250)
}

function gotoVacancy(id: string): void {
  visible.value = false
  router.push({ name: ROUTE_NAMES.VACANCY_DETAIL, params: { id } })
}

function gotoCandidate(id: string): void {
  visible.value = false
  router.push({ name: ROUTE_NAMES.CANDIDATE_DETAIL, params: { id } })
}

const hasResults = () => results.value.vacancies.length + results.value.candidates.length > 0
</script>

<template>
  <Dialog
    v-model:visible="visible"
    modal
    :closable="true"
    :show-header="false"
    :style="{ width: '90%', maxWidth: '600px' }"
    :pt="{ root: { class: 'overflow-hidden' }, content: { class: 'p-0' } }"
  >
    <div class="flex items-center gap-2 border-b border-gray-100 px-4 py-3">
      <i class="pi pi-search text-gray-400"></i>
      <InputText
        ref="inputRef"
        v-model="query"
        :placeholder="t('common.searchPlaceholder')"
        class="flex-1 border-0 shadow-none focus:ring-0"
        :pt="{
          root: { class: 'border-0 shadow-none focus:shadow-none focus:ring-0 px-0 text-base' },
        }"
        @input="onInput"
        @keyup.escape="visible = false"
      />
      <kbd
        class="hidden rounded border border-gray-200 bg-gray-50 px-1.5 py-0.5 text-[10px] font-medium text-gray-500 sm:inline"
        >ESC</kbd
      >
    </div>

    <div class="max-h-96 overflow-y-auto">
      <div v-if="loading" class="px-4 py-8 text-center text-sm text-gray-400">
        <i class="pi pi-spinner pi-spin mr-2"></i>{{ t('common.loading') }}
      </div>

      <div v-else-if="!query.trim()" class="px-4 py-8 text-center text-sm text-gray-400">
        {{ t('common.searchHint') }}
      </div>

      <div v-else-if="!hasResults()" class="px-4 py-8 text-center text-sm text-gray-400">
        {{ t('common.noResults') }}
      </div>

      <template v-else>
        <div v-if="results.vacancies.length > 0">
          <div
            class="px-4 pb-1 pt-3 text-[10px] font-semibold uppercase tracking-widest text-gray-400"
          >
            {{ t('nav.vacancies') }}
          </div>
          <button
            v-for="v in results.vacancies"
            :key="`v-${v.id}`"
            class="flex w-full items-center gap-3 px-4 py-2 text-left hover:bg-blue-50"
            @click="gotoVacancy(v.id)"
          >
            <i class="pi pi-briefcase text-sm text-blue-500"></i>
            <span class="flex-1 truncate text-sm font-medium text-gray-900">{{ v.title }}</span>
            <span class="text-xs text-gray-400">{{ v.status }}</span>
          </button>
        </div>

        <div v-if="results.candidates.length > 0">
          <div
            class="px-4 pb-1 pt-3 text-[10px] font-semibold uppercase tracking-widest text-gray-400"
          >
            {{ t('nav.candidates') }}
          </div>
          <button
            v-for="c in results.candidates"
            :key="`c-${c.id}`"
            class="flex w-full items-center gap-3 px-4 py-2 text-left hover:bg-blue-50"
            @click="gotoCandidate(c.id)"
          >
            <i class="pi pi-user text-sm text-emerald-500"></i>
            <div class="min-w-0 flex-1">
              <p class="truncate text-sm font-medium text-gray-900">{{ c.candidateName }}</p>
              <p class="truncate text-xs text-gray-500">
                {{ c.candidateEmail }} · {{ c.vacancyTitle }}
              </p>
            </div>
            <span class="text-xs text-gray-400">{{ c.status }}</span>
          </button>
        </div>
      </template>
    </div>
  </Dialog>
</template>
