<script setup lang="ts">
import VacancyDetailPage from '@/features/vacancies/pages/VacancyDetailPage.vue'
import { USER_ROLES } from '@/shared/constants/roles'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.VACANCY_DETAIL,
  layout: 'app',
  requiresAuth: true,
  roles: [USER_ROLES.ADMIN, USER_ROLES.HR],
})
</script>

<template>
  <VacancyDetailPage />
</template>
