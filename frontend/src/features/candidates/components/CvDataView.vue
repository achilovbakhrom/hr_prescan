<script setup lang="ts">
import Tag from 'primevue/tag'
import type { CvParsedData } from '../types/candidate.types'

defineProps<{
  data: CvParsedData
}>()
</script>

<template>
  <div class="space-y-6">
    <!-- Skills -->
    <div>
      <h3 class="mb-2 text-sm font-semibold text-gray-600">Skills</h3>
      <div v-if="data.skills.length > 0" class="flex flex-wrap gap-2">
        <Tag
          v-for="skill in data.skills"
          :key="skill"
          :value="skill"
          severity="info"
        />
      </div>
      <p v-else class="text-sm text-gray-400">No skills extracted</p>
    </div>

    <!-- Experience -->
    <div>
      <h3 class="mb-2 text-sm font-semibold text-gray-600">Experience</h3>
      <div
        v-if="data.experience.length > 0"
        class="space-y-3 border-l-2 border-blue-200 pl-4"
      >
        <div
          v-for="(entry, idx) in data.experience"
          :key="idx"
          class="relative"
        >
          <div
            class="absolute -left-[1.35rem] top-1 h-2.5 w-2.5 rounded-full bg-blue-500"
          ></div>
          <p class="font-medium">{{ entry.position }}</p>
          <p class="text-sm text-gray-600">
            {{ entry.company }}
            <span v-if="entry.duration" class="text-gray-400">
              &middot; {{ entry.duration }}
            </span>
          </p>
          <p v-if="entry.description" class="mt-1 text-sm text-gray-500">
            {{ entry.description }}
          </p>
        </div>
      </div>
      <p v-else class="text-sm text-gray-400">No experience extracted</p>
    </div>

    <!-- Education -->
    <div>
      <h3 class="mb-2 text-sm font-semibold text-gray-600">Education</h3>
      <div v-if="data.education.length > 0" class="space-y-3">
        <div
          v-for="(entry, idx) in data.education"
          :key="idx"
          class="rounded border border-gray-100 bg-gray-50 p-3"
        >
          <p class="font-medium">{{ entry.degree }} in {{ entry.field }}</p>
          <p class="text-sm text-gray-600">
            {{ entry.institution }}
            <span v-if="entry.year" class="text-gray-400">
              &middot; {{ entry.year }}
            </span>
          </p>
        </div>
      </div>
      <p v-else class="text-sm text-gray-400">No education extracted</p>
    </div>
  </div>
</template>
