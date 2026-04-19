<script setup lang="ts">
/**
 * MyCvsPage — list of generated CVs plus profile summary card.
 * Glass section wrappers, empty state in glass-dashed surface.
 * Page logic lives in `useMyCvs` composable.
 */
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import Message from 'primevue/message'
import ConfirmDialog from 'primevue/confirmdialog'
import GlassCard from '@/shared/components/GlassCard.vue'
import CvProfileCard from '../components/CvProfileCard.vue'
import CvFileCard from '../components/CvFileCard.vue'
import { useMyCvs } from '../composables/useMyCvs'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const { t } = useI18n()
const router = useRouter()

const {
  profile,
  cvs,
  loading,
  error,
  actionLoading,
  successMessage,
  fetchData,
  viewCv,
  viewPublicCv,
  toggleVisibility,
  handleToggleActive,
  handleDeleteProfile,
  handleDelete,
} = useMyCvs()

const hasProfileData = computed(() =>
  profile.value ? profile.value.completeness.score > 0 : false,
)

onMounted(fetchData)
</script>

<template>
  <div class="mx-auto max-w-4xl space-y-6">
    <header class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h1 class="text-3xl font-semibold tracking-tight text-[color:var(--color-text-primary)]">
          {{ t('myCvs.title') }}
        </h1>
        <p class="mt-1 text-sm text-[color:var(--color-text-muted)]">
          {{ t('myCvs.subtitle') || 'Your profile and generated CV files.' }}
        </p>
      </div>
      <Button
        :label="t('myCvs.goToBuilder')"
        icon="pi pi-pencil"
        size="small"
        @click="router.push({ name: ROUTE_NAMES.CV_BUILDER })"
      />
    </header>

    <Message v-if="successMessage" severity="success">{{ successMessage }}</Message>
    <Message v-if="error" severity="error">{{ error }}</Message>

    <div v-if="loading" class="py-16 text-center">
      <i class="pi pi-spinner pi-spin text-3xl text-[color:var(--color-text-muted)]"></i>
    </div>

    <template v-else>
      <CvProfileCard
        v-if="profile"
        :profile="profile"
        @toggle-visibility="toggleVisibility"
        @view-public="viewPublicCv"
        @delete="handleDeleteProfile"
      />

      <GlassCard v-if="!hasProfileData && cvs.length === 0" class="!p-10 text-center">
        <i class="pi pi-file-pdf mb-4 text-5xl text-[color:var(--color-text-muted)]"></i>
        <p class="text-base font-semibold text-[color:var(--color-text-secondary)]">
          {{ t('myCvs.empty') }}
        </p>
        <p class="mt-1.5 text-sm text-[color:var(--color-text-muted)]">
          {{ t('myCvs.emptyHint') }}
        </p>
        <Button
          :label="t('myCvs.goToBuilder')"
          icon="pi pi-pencil"
          size="small"
          class="mt-5"
          @click="router.push({ name: ROUTE_NAMES.CV_BUILDER })"
        />
      </GlassCard>

      <section v-if="cvs.length > 0">
        <h2
          class="mb-3 text-xs font-semibold uppercase tracking-wider text-[color:var(--color-text-muted)]"
        >
          {{ t('myCvs.generatedPdfs') }}
        </h2>
        <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
          <CvFileCard
            v-for="cv in cvs"
            :key="cv.id"
            :cv="cv"
            :action-loading="actionLoading"
            @view="viewCv"
            @toggle-active="handleToggleActive"
            @delete="handleDelete"
          />
        </div>
      </section>
    </template>

    <ConfirmDialog />
  </div>
</template>
