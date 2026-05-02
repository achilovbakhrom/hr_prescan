/**
 * Field-level errors from DRF validation responses.
 * Keys are camelCase field names, values are the first error message for that field.
 */
export type FieldErrors = Record<string, string>

/**
 * Custom error class that carries both a human-readable message and field-level errors.
 */
export class ApiValidationError extends Error {
  fieldErrors: FieldErrors

  constructor(message: string, fieldErrors: FieldErrors) {
    super(message)
    this.name = 'ApiValidationError'
    this.fieldErrors = fieldErrors
  }
}

/**
 * Convert a snake_case string to camelCase.
 */
function toCamelCase(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter: string) => letter.toUpperCase())
}

/**
 * Extract field-level validation errors from a DRF error response.
 *
 * DRF returns errors like:
 *   { "company_name": ["This field is required."], "start_date": ["Invalid date."] }
 * or nested:
 *   { "non_field_errors": ["Some error"] }
 *
 * Returns a flat Record<string, string> with camelCase keys and the first error message.
 */
export function extractFieldErrors(err: unknown): FieldErrors {
  const data = getResponseData(err)
  if (!data || typeof data !== 'object' || Array.isArray(data)) return {}

  const errors: FieldErrors = {}
  for (const [key, value] of Object.entries(data as Record<string, unknown>)) {
    if (key === 'detail' || key === 'message') continue
    const camelKey = toCamelCase(key)
    if (Array.isArray(value) && value.length > 0 && typeof value[0] === 'string') {
      errors[camelKey] = value[0]
    } else if (typeof value === 'string') {
      errors[camelKey] = value
    }
  }
  return errors
}

/**
 * Extract a human-readable error message from an Axios error or generic Error.
 * If the response contains field-level errors, throws an ApiValidationError
 * with both the summary message and the field errors map.
 */
export function extractErrorMessage(err: unknown): string {
  const data = getResponseData(err)

  if (data && typeof data === 'object' && !Array.isArray(data)) {
    const obj = data as Record<string, unknown>

    // Direct message or detail
    if (typeof obj.message === 'string') return obj.message
    if (typeof obj.detail === 'string') return obj.detail

    // Field-level errors — build a summary message from first error
    const fieldErrors = extractFieldErrors(err)
    if (Object.keys(fieldErrors).length > 0) {
      const firstMsg = Object.values(fieldErrors)[0]
      return firstMsg
    }
  }

  if (err instanceof Error) {
    return err.message
  }
  return 'An unexpected error occurred'
}

export function getApiErrorMessage(err: unknown, fallback: string): string {
  const message = extractErrorMessage(err)
  return message === 'An unexpected error occurred' ? fallback : message
}

/**
 * Extract error details as an ApiValidationError if field-level errors exist,
 * otherwise returns a plain Error with the message.
 */
export function extractApiError(err: unknown): Error {
  const fieldErrors = extractFieldErrors(err)
  const message = extractErrorMessage(err)

  if (Object.keys(fieldErrors).length > 0) {
    return new ApiValidationError(message, fieldErrors)
  }
  return new Error(message)
}

function getResponseData(err: unknown): unknown {
  if (
    typeof err === 'object' &&
    err !== null &&
    'response' in err &&
    typeof (err as Record<string, unknown>).response === 'object'
  ) {
    return (err as { response: { data?: unknown } }).response.data
  }
  return null
}
