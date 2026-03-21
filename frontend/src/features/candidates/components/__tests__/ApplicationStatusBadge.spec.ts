import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ApplicationStatusBadge from '../ApplicationStatusBadge.vue'
import type { ApplicationStatus } from '../../types/candidate.types'

const STATUS_LABELS: Record<ApplicationStatus, string> = {
  applied: 'Applied',
  prescanned: 'Prescanned',
  interviewed: 'Interviewed',
  shortlisted: 'Shortlisted',
  hired: 'Hired',
  rejected: 'Rejected',
  expired: 'Expired',
  archived: 'Archived',
}

describe('ApplicationStatusBadge', () => {
  const statuses = Object.keys(STATUS_LABELS) as ApplicationStatus[]

  statuses.forEach((status) => {
    it(`renders correct label for "${status}" status`, () => {
      const wrapper = mount(ApplicationStatusBadge, {
        props: { status },
        global: {
          stubs: {
            Tag: {
              template: '<span>{{ value }}</span>',
              props: ['value', 'severity'],
            },
          },
        },
      })

      expect(wrapper.text()).toContain(STATUS_LABELS[status])
    })
  })

  it('passes correct severity for success statuses', () => {
    const wrapper = mount(ApplicationStatusBadge, {
      props: { status: 'hired' as ApplicationStatus },
      global: {
        stubs: {
          Tag: {
            template: '<span :data-severity="severity">{{ value }}</span>',
            props: ['value', 'severity'],
          },
        },
      },
    })

    const tag = wrapper.find('span')
    expect(tag.attributes('data-severity')).toBe('success')
  })

  it('passes correct severity for danger statuses', () => {
    const wrapper = mount(ApplicationStatusBadge, {
      props: { status: 'rejected' as ApplicationStatus },
      global: {
        stubs: {
          Tag: {
            template: '<span :data-severity="severity">{{ value }}</span>',
            props: ['value', 'severity'],
          },
        },
      },
    })

    const tag = wrapper.find('span')
    expect(tag.attributes('data-severity')).toBe('danger')
  })

  it('passes correct severity for secondary statuses', () => {
    const wrapper = mount(ApplicationStatusBadge, {
      props: { status: 'archived' as ApplicationStatus },
      global: {
        stubs: {
          Tag: {
            template: '<span :data-severity="severity">{{ value }}</span>',
            props: ['value', 'severity'],
          },
        },
      },
    })

    const tag = wrapper.find('span')
    expect(tag.attributes('data-severity')).toBe('secondary')
  })
})
