<script setup lang="ts">
import InputText from 'primevue/inputtext'

defineProps<{
  linkedinUrl: string
  githubUrl: string
  websiteUrl: string
  fieldErrors: Record<string, string>
}>()

const emit = defineEmits<{
  'update:linkedinUrl': [value: string]
  'update:githubUrl': [value: string]
  'update:websiteUrl': [value: string]
}>()

function hasError(field: string): boolean {
  return field in (arguments[0] ?? {})
}
</script>

<template>
  <div class="grid grid-cols-1 gap-5 sm:grid-cols-3">
    <div class="flex flex-col gap-1">
      <label for="linkedinUrl" class="text-sm font-medium text-gray-700">
        LinkedIn
      </label>
      <InputText
        id="linkedinUrl"
        :model-value="linkedinUrl"
        placeholder="https://linkedin.com/in/..."
        class="w-full"
        :invalid="'linkedinUrl' in fieldErrors"
        @update:model-value="emit('update:linkedinUrl', $event as string)"
      />
      <small v-if="'linkedinUrl' in fieldErrors" class="text-red-500">{{ fieldErrors.linkedinUrl }}</small>
    </div>

    <div class="flex flex-col gap-1">
      <label for="githubUrl" class="text-sm font-medium text-gray-700">
        GitHub
      </label>
      <InputText
        id="githubUrl"
        :model-value="githubUrl"
        placeholder="https://github.com/..."
        class="w-full"
        :invalid="'githubUrl' in fieldErrors"
        @update:model-value="emit('update:githubUrl', $event as string)"
      />
      <small v-if="'githubUrl' in fieldErrors" class="text-red-500">{{ fieldErrors.githubUrl }}</small>
    </div>

    <div class="flex flex-col gap-1">
      <label for="websiteUrl" class="text-sm font-medium text-gray-700">
        Website
      </label>
      <InputText
        id="websiteUrl"
        :model-value="websiteUrl"
        placeholder="https://..."
        class="w-full"
        :invalid="'websiteUrl' in fieldErrors"
        @update:model-value="emit('update:websiteUrl', $event as string)"
      />
      <small v-if="'websiteUrl' in fieldErrors" class="text-red-500">{{ fieldErrors.websiteUrl }}</small>
    </div>
  </div>
</template>
