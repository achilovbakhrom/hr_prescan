<script setup lang="ts">
import { USER_ROLES } from '@/shared/constants/roles'
import { ROUTE_NAMES } from '@/shared/constants/routes'

definePageMeta({
  name: ROUTE_NAMES.CANDIDATE_BASE,
  layout: 'app',
  requiresAuth: true,
  roles: [USER_ROLES.ADMIN, USER_ROLES.HR],
})

void navigateTo({ name: ROUTE_NAMES.CANDIDATE_LIST, query: { tab: 'base' } }, { replace: true })
</script>
