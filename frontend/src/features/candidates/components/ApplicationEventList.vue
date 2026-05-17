<script setup lang="ts">
import type { ApplicationEvent } from '../types/candidate.types'

defineProps<{
  events: ApplicationEvent[]
}>()

function formatDate(value: string): string {
  return new Date(value).toLocaleString([], {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function iconFor(type: string): string {
  if (type === 'share_link_rotated') return 'pi pi-refresh'
  return 'pi pi-comment'
}
</script>

<template>
  <div class="space-y-3">
    <h3 class="text-sm font-semibold text-gray-600">Collaboration activity</h3>
    <p v-if="!events.length" class="text-sm text-gray-400">No collaboration activity yet.</p>
    <div v-for="event in events" :key="event.id" class="flex gap-3 rounded-lg bg-gray-50 p-3">
      <span
        class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-50 text-blue-600"
      >
        <i :class="iconFor(event.eventType)"></i>
      </span>
      <div class="min-w-0 flex-1">
        <p class="text-sm font-medium text-gray-800">{{ event.message }}</p>
        <p class="text-xs text-gray-500">
          {{ event.actorName || 'System' }} · {{ formatDate(event.createdAt) }}
        </p>
      </div>
    </div>
  </div>
</template>
