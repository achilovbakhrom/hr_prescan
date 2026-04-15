<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import Message from 'primevue/message'
import Tag from 'primevue/tag'
import SkillAutocomplete from '@/shared/components/SkillAutocomplete.vue'
import { useCvBuilderStore } from '../stores/cv-builder.store'

const { t } = useI18n()
const store = useCvBuilderStore()

const successMessage = ref<string | null>(null)
const errorMessage = ref<string | null>(null)

const selectedSlugs = ref<string[]>([])

const currentSkills = computed(() => store.profile?.skills ?? [])

watch(
  () => store.profile?.skills,
  (skills) => {
    if (skills) {
      selectedSlugs.value = skills.map((s) => s.slug)
    }
  },
  { immediate: true },
)

async function handleSave(): Promise<void> {
  successMessage.value = null
  errorMessage.value = null

  try {
    await store.updateSkills(selectedSlugs.value)
    successMessage.value = t('cvBuilder.skills.saveSuccess')
  } catch (err: unknown) {
    errorMessage.value = err instanceof Error ? err.message : t('common.error')
  }
}
</script>

<template>
  <div>
    <Message v-if="successMessage" severity="success" class="mb-4">
      {{ successMessage }}
    </Message>
    <Message v-if="errorMessage" severity="error" class="mb-4">
      {{ errorMessage }}
    </Message>

    <div class="flex flex-col gap-4">
      <div v-if="currentSkills.length" class="flex flex-wrap gap-2">
        <Tag v-for="skill in currentSkills" :key="skill.slug" :value="skill.name" severity="info" />
      </div>

      <div v-if="!currentSkills.length" class="py-4 text-center text-sm text-gray-500">
        {{ t('cvBuilder.skills.empty') }}
      </div>

      <div class="flex flex-col gap-1">
        <label class="text-sm font-medium text-gray-700">
          {{ t('cvBuilder.skills.selectSkills') }}
        </label>
        <SkillAutocomplete v-model="selectedSlugs" />
      </div>

      <div class="flex justify-end pt-2">
        <Button :label="t('common.save')" :loading="store.saving" @click="handleSave" />
      </div>
    </div>
  </div>
</template>
