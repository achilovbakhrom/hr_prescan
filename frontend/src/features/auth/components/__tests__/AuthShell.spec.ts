import { describe, expect, it, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AuthShell from '../AuthShell.vue'

const globalConfig = {
  stubs: {
    RouterLink: {
      template: '<a :data-to="JSON.stringify(to)"><slot /></a>',
      props: ['to'],
    },
    GlassCard: {
      template: '<section><slot /><slot name="footer" /></section>',
    },
  },
}

describe('AuthShell', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders the full brand logo as a link to the public home page', () => {
    const wrapper = mount(AuthShell, { global: globalConfig })

    const homeLink = wrapper.findAll('a').find((link) => link.attributes('data-to') === '"/"')
    expect(homeLink).toBeDefined()
    expect(homeLink!.text()).toContain('PreScreen AI')
  })
})
