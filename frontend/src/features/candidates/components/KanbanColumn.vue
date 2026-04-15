<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Menu from 'primevue/menu'
import { ref } from 'vue'
import KanbanCard from './KanbanCard.vue'
import type { Application, ApplicationStatus } from '../types/candidate.types'

export interface ColumnDef {
  status: ApplicationStatus
  label: string
  color: string
  bgColor: string
  borderColor: string
  dotColor: string
}

const props = defineProps<{
  column: ColumnDef
  candidates: Application[]
  menuItems: { label: string; icon: string; command: () => void; separator?: boolean }[]
}>()

const emit = defineEmits<{
  drop: [event: DragEvent]
  dragover: [event: DragEvent]
  viewCandidate: [candidate: Application]
  dragStart: [event: DragEvent, candidate: Application]
}>()

const { t } = useI18n()
const menuRef = ref<InstanceType<typeof Menu> | null>(null)

function toggleMenu(event: Event): void {
  menuRef.value?.toggle(event)
}

function onDragOver(event: DragEvent): void {
  event.preventDefault()
  emit('dragover', event)
}
</script>

<template>
  <div
    class="flex w-56 shrink-0 flex-col rounded-xl border border-gray-100 bg-gray-50/50 sm:w-64"
    @drop="emit('drop', $event)"
    @dragover="onDragOver"
  >
    <!-- Column header -->
    <div class="flex items-center justify-between px-4 py-3">
      <div class="flex items-center gap-2">
        <div class="h-2 w-2 rounded-full" :class="column.dotColor"></div>
        <span class="text-sm font-semibold text-gray-700">{{ column.label }}</span>
        <span
          class="flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-xs font-medium"
          :class="[column.bgColor, column.color]"
        >
          {{ candidates.length }}
        </span>
      </div>
      <button
        class="rounded p-1 text-gray-400 hover:bg-gray-200 hover:text-gray-600"
        @click="toggleMenu($event)"
      >
        <i class="pi pi-ellipsis-v text-xs"></i>
      </button>
      <Menu
        ref="menuRef"
        :model="menuItems"
        :popup="true"
      />
    </div>

    <!-- Cards -->
    <div class="flex flex-1 flex-col gap-2 px-3 pb-3" style="min-height: 120px">
      <KanbanCard
        v-for="candidate in candidates"
        :key="candidate.id"
        :candidate="candidate"
        :column="column"
        @click="emit('viewCandidate', candidate)"
        @drag-start="emit('dragStart', $event, candidate)"
      />

      <!-- Empty state -->
      <div
        v-if="candidates.length === 0"
        class="flex flex-1 items-center justify-center rounded-lg border border-dashed border-gray-200 py-6"
      >
        <p class="text-xs text-gray-400">{{ t('candidates.noCandidates') }}</p>
      </div>
    </div>
  </div>
</template>
