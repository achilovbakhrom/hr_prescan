<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Tag from 'primevue/tag'
import ToggleSwitch from 'primevue/toggleswitch'
import Button from 'primevue/button'
import Dialog from 'primevue/dialog'
import Checkbox from 'primevue/checkbox'
import type { TeamMember } from '../types/settings.types'
import { ALL_HR_PERMISSIONS, type HRPermission } from '@/shared/types/auth.types'

const { t } = useI18n()

defineProps<{
  members: TeamMember[]
}>()

const emit = defineEmits<{
  toggleActive: [userId: string]
  updatePermissions: [userId: string, permissions: HRPermission[]]
}>()

const editingMember = ref<TeamMember | null>(null)
const editPermissions = ref<HRPermission[]>([])

const permissionOptions: { value: HRPermission; labelKey: string }[] = [
  { value: 'manage_vacancies', labelKey: 'permissions.manageVacancies' },
  { value: 'manage_candidates', labelKey: 'permissions.manageCandidates' },
  { value: 'manage_interviews', labelKey: 'permissions.manageInterviews' },
  { value: 'manage_team', labelKey: 'permissions.manageTeam' },
  { value: 'view_analytics', labelKey: 'permissions.viewAnalytics' },
  { value: 'manage_settings', labelKey: 'permissions.manageSettings' },
]

function getRoleSeverity(role: string): 'info' | 'warn' | undefined {
  if (role === 'admin') return 'warn'
  if (role === 'hr') return 'info'
  return undefined
}

function openPermissions(member: TeamMember): void {
  editingMember.value = member
  editPermissions.value = [...(member.hrPermissions || [])]
}

function savePermissions(): void {
  if (!editingMember.value) return
  emit('updatePermissions', editingMember.value.id, editPermissions.value)
  editingMember.value = null
}

function permissionCount(member: TeamMember): string {
  if (member.role === 'admin') return t('permissions.allPermissions')
  const count = (member.hrPermissions || []).length
  if (count === 0) return t('permissions.noPermissions')
  return `${count} / ${ALL_HR_PERMISSIONS.length}`
}
</script>

<template>
  <DataTable :value="members" striped-rows>
    <Column :header="t('admin.users.name')">
      <template #body="{ data }">
        {{ (data as TeamMember).firstName }}
        {{ (data as TeamMember).lastName }}
      </template>
    </Column>
    <Column field="email" :header="t('admin.users.email')" />
    <Column :header="t('settings.team.role')">
      <template #body="{ data }">
        <Tag
          :value="(data as TeamMember).role.toUpperCase()"
          :severity="getRoleSeverity((data as TeamMember).role)"
        />
      </template>
    </Column>
    <Column :header="t('permissions.title')">
      <template #body="{ data }">
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-600">{{ permissionCount(data as TeamMember) }}</span>
          <Button
            v-if="(data as TeamMember).role === 'hr'"
            icon="pi pi-pencil"
            text
            rounded
            size="small"
            @click="openPermissions(data as TeamMember)"
          />
        </div>
      </template>
    </Column>
    <Column :header="t('common.status')">
      <template #body="{ data }">
        <Tag
          :value="(data as TeamMember).isActive ? 'Active' : 'Inactive'"
          :severity="(data as TeamMember).isActive ? 'success' : 'danger'"
        />
      </template>
    </Column>
    <Column :header="t('common.actions')">
      <template #body="{ data }">
        <ToggleSwitch
          v-if="(data as TeamMember).role !== 'admin'"
          :model-value="(data as TeamMember).isActive"
          @update:model-value="emit('toggleActive', (data as TeamMember).id)"
        />
      </template>
    </Column>
  </DataTable>

  <!-- Edit permissions dialog -->
  <Dialog
    :visible="!!editingMember"
    :header="`${t('permissions.title')} — ${editingMember?.firstName} ${editingMember?.lastName}`"
    :modal="true"
    :style="{ width: '450px' }"
    @update:visible="!$event && (editingMember = null)"
  >
    <div class="flex flex-col gap-2">
      <label
        v-for="opt in permissionOptions"
        :key="opt.value"
        class="flex cursor-pointer items-center gap-3 rounded-md px-2 py-2 transition-colors hover:bg-gray-50"
      >
        <Checkbox
          v-model="editPermissions"
          :value="opt.value"
        />
        <span class="text-sm font-medium text-gray-800">{{ t(opt.labelKey) }}</span>
      </label>
    </div>
    <template #footer>
      <div class="flex justify-end gap-2">
        <Button
          :label="t('common.cancel')"
          severity="secondary"
          @click="editingMember = null"
        />
        <Button
          :label="t('settings.company.save')"
          @click="savePermissions"
        />
      </div>
    </template>
  </Dialog>
</template>
