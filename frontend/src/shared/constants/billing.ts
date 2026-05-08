export const BILLING_ENABLED = import.meta.env.VITE_BILLING_ENABLED === 'true'
export const FREE_ACCESS_ACTIVE_USER_TARGET = Number(
  import.meta.env.VITE_BILLING_FREE_ACCESS_ACTIVE_USER_TARGET ?? 500,
)
