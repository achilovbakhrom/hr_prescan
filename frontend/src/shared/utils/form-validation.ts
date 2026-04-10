import type { Schema, ValidationError } from 'yup'
import type { FieldErrors } from '@/shared/api/errors'

/**
 * Validate form data against a Yup schema.
 * Returns null on success, or a FieldErrors map on failure.
 */
export async function validateForm(
  schema: Schema,
  data: Record<string, unknown>,
): Promise<FieldErrors | null> {
  try {
    await schema.validate(data, { abortEarly: false })
    return null
  } catch (err: unknown) {
    const validationError = err as ValidationError
    const errors: FieldErrors = {}
    for (const inner of validationError.inner) {
      if (inner.path && !errors[inner.path]) {
        errors[inner.path] = inner.message
      }
    }
    return errors
  }
}
