function normalizeTelegramUsername(raw?: string): string {
  return (raw ?? '').trim().replace(/^@/, '')
}

export function getCandidateTelegramBotUsername(override?: string): string {
  if (override) return normalizeTelegramUsername(override)

  return normalizeTelegramUsername(
    (import.meta.env.VITE_TELEGRAM_CANDIDATE_BOT_USERNAME as string | undefined) ??
      (import.meta.env.VITE_TELEGRAM_BOT_USERNAME as string | undefined),
  )
}

export function getHrTelegramBotUsername(override?: string): string {
  if (override) return normalizeTelegramUsername(override)

  return normalizeTelegramUsername(
    import.meta.env.VITE_TELEGRAM_HR_BOT_USERNAME as string | undefined,
  )
}

export function buildCandidateTelegramBotUrl(
  prescanToken?: string | null,
  telegramCode?: number | null,
  usernameOverride?: string,
): string {
  const username = getCandidateTelegramBotUsername(usernameOverride)
  if (!username) return ''
  if (prescanToken) return `https://t.me/${username}?start=ps_${prescanToken}`
  if (telegramCode) return `https://t.me/${username}?start=vac_${telegramCode}`
  return `https://t.me/${username}`
}

export function buildHrTelegramBotUrl(usernameOverride?: string): string {
  const username = getHrTelegramBotUsername(usernameOverride)
  if (!username) return ''
  return `https://t.me/${username}`
}
