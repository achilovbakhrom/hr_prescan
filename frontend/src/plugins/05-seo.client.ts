import { installSeoRouterGuards } from '@/shared/seo/routeSeo'

export default defineNuxtPlugin(() => {
  installSeoRouterGuards(useRouter())
})
