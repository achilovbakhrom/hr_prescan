<script setup lang="ts">
import VacancyListPage from '@/features/vacancies/pages/VacancyListPage.vue'
import { USER_ROLES } from '@/shared/constants/roles'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.VACANCY_LIST,
  layout: 'app',
  requiresAuth: true,
  roles: [USER_ROLES.ADMIN, USER_ROLES.HR],
})
</script>

<template>
  <VacancyListPage />
</template>
