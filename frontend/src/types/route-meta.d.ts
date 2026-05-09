import type { UserRole } from '@/shared/types/auth.types'
import type { RouteSeoMeta } from '@/shared/seo/routeSeo'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    roles?: UserRole[]
    seo?: RouteSeoMeta
  }
}

export {}
