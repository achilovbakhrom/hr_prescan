import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import RegisterPage from '../RegisterPage.vue'
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
      props: ['inputId', 'modelValue', 'placeholder', 'feedback', 'toggleMask', 'invalid', 'inputClass'],
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

describe('RegisterPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders registration form fields', () => {
    const wrapper = shallowMount(RegisterPage, { global: globalConfig })

    const firstNameInput = wrapper.find('#firstName')
    expect(firstNameInput.exists()).toBe(true)

    const lastNameInput = wrapper.find('#lastName')
    expect(lastNameInput.exists()).toBe(true)

    const emailInput = wrapper.find('#email')
    expect(emailInput.exists()).toBe(true)

    const passwordInput = wrapper.find('#password')
    expect(passwordInput.exists()).toBe(true)

    expect(wrapper.find('form').exists()).toBe(true)
    expect(wrapper.text()).toContain('Create Account')
  })

  it('shows link to login page', () => {
    const wrapper = shallowMount(RegisterPage, { global: globalConfig })

    const links = wrapper.findAll('a')
    const loginLink = links.find((link) => {
      const to = link.attributes('data-to')
      return to && to.includes(ROUTE_NAMES.LOGIN)
    })
    expect(loginLink).toBeDefined()
    expect(loginLink!.text()).toBe('Login')
  })
})
