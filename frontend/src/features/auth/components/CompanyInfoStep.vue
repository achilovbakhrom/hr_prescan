<script setup lang="ts">
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import Button from 'primevue/button'
import type { CompanySize } from '../types/auth.types'

interface SizeOption {
  label: string
  value: CompanySize
}

defineProps<{
  companyName: string
  industry: string
  size: CompanySize | null
  country: string
  submitted: boolean
  errors: {
    companyName: boolean
    industry: boolean
    size: boolean
    country: boolean
  }
  sizeOptions: SizeOption[]
}>()

const emit = defineEmits<{
  'update:companyName': [value: string]
  'update:industry': [value: string]
  'update:size': [value: CompanySize | null]
  'update:country': [value: string]
  next: []
}>()
</script>

<template>
  <form class="flex flex-col gap-4 pt-4" @submit.prevent="emit('next')">
    <div class="flex flex-col gap-1">
      <label for="companyName" class="text-sm font-medium text-gray-700">
        Company Name
      </label>
      <InputText
        id="companyName"
        :model-value="companyName"
        placeholder="Enter company name"
        :invalid="submitted && errors.companyName"
        class="w-full"
        @update:model-value="emit('update:companyName', $event as string)"
      />
      <small v-if="submitted && errors.companyName" class="text-red-500">
        Company name is required.
      </small>
    </div>

    <div class="flex flex-col gap-1">
      <label for="industry" class="text-sm font-medium text-gray-700">
        Industry
      </label>
      <InputText
        id="industry"
        :model-value="industry"
        placeholder="e.g. Technology, Healthcare, Finance"
        :invalid="submitted && errors.industry"
        class="w-full"
        @update:model-value="emit('update:industry', $event as string)"
      />
      <small v-if="submitted && errors.industry" class="text-red-500">
        Industry is required.
      </small>
    </div>

    <div class="flex flex-col gap-1">
      <label for="size" class="text-sm font-medium text-gray-700">
        Company Size
      </label>
      <Select
        id="size"
        :model-value="size"
        :options="sizeOptions"
        option-label="label"
        option-value="value"
        placeholder="Select company size"
        :invalid="submitted && errors.size"
        class="w-full"
        @update:model-value="emit('update:size', $event as CompanySize)"
      />
      <small v-if="submitted && errors.size" class="text-red-500">
        Company size is required.
      </small>
    </div>

    <div class="flex flex-col gap-1">
      <label for="country" class="text-sm font-medium text-gray-700">
        Country
      </label>
      <InputText
        id="country"
        :model-value="country"
        placeholder="Enter country"
        :invalid="submitted && errors.country"
        class="w-full"
        @update:model-value="emit('update:country', $event as string)"
      />
      <small v-if="submitted && errors.country" class="text-red-500">
        Country is required.
      </small>
    </div>

    <div class="flex justify-end pt-2">
      <Button type="submit" label="Next" icon="pi pi-arrow-right" icon-pos="right" />
    </div>
  </form>
</template>
