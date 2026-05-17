<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { useConfirm } from 'primevue/useconfirm'

const props = defineProps<{
  candidateName: string
  interviewEnabled?: boolean
  loading: boolean
}>()

const emit = defineEmits<{
  resetScreening: [sessionType: 'prescanning' | 'interview']
}>()

const { t } = useI18n()
const confirm = useConfirm()

function confirmResetScreening(sessionType: 'prescanning' | 'interview'): void {
  const isPrescanning = sessionType === 'prescanning'
  confirm.require({
    message: t(
      isPrescanning
        ? 'candidates.dialogs.msgClearPrescanning'
        : 'candidates.dialogs.msgClearInterview',
      { name: props.candidateName },
    ),
    header: t(
      isPrescanning
        ? 'candidates.dialogs.clearPrescanningHeader'
        : 'candidates.dialogs.clearInterviewHeader',
    ),
    icon: 'pi pi-refresh',
    acceptLabel: t('candidates.dialogs.yesClearSession'),
    rejectLabel: t('common.cancel'),
    accept: () => emit('resetScreening', sessionType),
  })
}
</script>

<template>
  <Button
    :label="t('candidates.actions.clearPrescanning')"
    icon="pi pi-refresh"
    size="small"
    severity="secondary"
    outlined
    :disabled="loading"
    @click="confirmResetScreening('prescanning')"
  />
  <Button
    v-if="interviewEnabled"
    :label="t('candidates.actions.clearInterview')"
    icon="pi pi-refresh"
    size="small"
    severity="secondary"
    outlined
    :disabled="loading"
    @click="confirmResetScreening('interview')"
  />
</template>
