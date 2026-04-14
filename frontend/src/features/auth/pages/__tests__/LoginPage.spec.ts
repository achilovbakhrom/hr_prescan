import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import LoginPage from '../LoginPage.vue'
import { createPinia, setActivePinia } from 'pinia'
import { ROUTE_NAMES } from '@/shared/constants/routes'

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn(),
    currentRoute: { value: { query: {} } },
  }),
}))

const globalConfig = {
  stubs: {
    RouterLink: {
      template: '<a :data-to="JSON.stringify(to)"><slot /></a>',
      props: ['to'],
    },
    InputText: {
      template: '<input :id="id" :type="type" :placeholder="placeholder" />',
      props: ['id', 'type', 'modelValue', 'placeholder', 'invalid'],
    },
    Password: {
      template: '<input :id="inputId" type="password" :placeholder="placeholder" />',
      props: [
        'inputId',
        'modelValue',
        'placeholder',
        'feedback',
        'toggleMask',
        'invalid',
        'inputClass',
      ],
    },
    Button: {
      template: '<button :type="type">{{ label }}</button>',
      props: ['type', 'label', 'loading'],
    },
    Message: {
      template: '<div><slot /></div>',
      props: ['severity'],
    },
    GoogleSignInButton: {
      template: '<div data-testid="google-sign-in">Google Sign In</div>',
    },
  },
}

describe('LoginPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders login form with email and password inputs', () => {
    const wrapper = shallowMount(LoginPage, { global: globalConfig })

    const emailInput = wrapper.find('#email')
    expect(emailInput.exists()).toBe(true)

    const passwordInput = wrapper.find('#password')
    expect(passwordInput.exists()).toBe(true)

    expect(wrapper.find('form').exists()).toBe(true)
    expect(wrapper.text()).toContain('Sign In')
  })

  it('renders Google sign-in button', () => {
    const wrapper = shallowMount(LoginPage, { global: globalConfig })

    const googleBtn = wrapper.find('[data-testid="google-sign-in"]')
    expect(googleBtn.exists()).toBe(true)
  })

  it('shows link to register page', () => {
    const wrapper = shallowMount(LoginPage, { global: globalConfig })

    const links = wrapper.findAll('a')
    const registerLink = links.find((link) => {
      const to = link.attributes('data-to')
      return to && to.includes(ROUTE_NAMES.REGISTER)
    })
    expect(registerLink).toBeDefined()
    expect(registerLink!.text()).toBe('Register')
  })

  it('shows link to company register page', () => {
    const wrapper = shallowMount(LoginPage, { global: globalConfig })

    const links = wrapper.findAll('a')
    const companyLink = links.find((link) => {
      const to = link.attributes('data-to')
      return to && to.includes(ROUTE_NAMES.COMPANY_REGISTER)
    })
    expect(companyLink).toBeDefined()
    expect(companyLink!.text()).toBe('Register your company')
  })
})
