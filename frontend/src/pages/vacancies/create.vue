<script setup lang="ts">
import VacancyCreatePage from '@/features/vacancies/pages/VacancyCreatePage.vue'
import { USER_ROLES } from '@/shared/constants/roles'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.VACANCY_CREATE,
  layout: 'app',
  requiresAuth: true,
  roles: [USER_ROLES.ADMIN, USER_ROLES.HR],
})
</script>

<template>
  <VacancyCreatePage />
</template>
