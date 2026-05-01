/**
 * Convert camelCase keys to snake_case (Django convention).
 */
function toSnakeCase(str: string): string {
  return str.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`)
}

export function convertKeysToSnakeCase(obj: unknown): unknown {
  if (Array.isArray(obj)) {
    return obj.map(convertKeysToSnakeCase)
  }
  if (
    obj !== null &&
    typeof obj === 'object' &&
    !(obj instanceof File) &&
    !(obj instanceof Blob) &&
    !(obj instanceof FormData)
  ) {
    return Object.fromEntries(
      Object.entries(obj as Record<string, unknown>).map(([key, value]) => [
        toSnakeCase(key),
        convertKeysToSnakeCase(value),
      ]),
    )
  }
  return obj
}

/**
 * Convert snake_case keys to camelCase (frontend convention).
 */
function toCamelCase(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter: string) => letter.toUpperCase())
}

export function convertKeysToCamelCase(obj: unknown): unknown {
  if (Array.isArray(obj)) {
    return obj.map(convertKeysToCamelCase)
  }
  if (obj !== null && typeof obj === 'object') {
    return Object.fromEntries(
      Object.entries(obj as Record<string, unknown>).map(([key, value]) => [
        toCamelCase(key),
        convertKeysToCamelCase(value),
      ]),
    )
  }
  return obj
}
