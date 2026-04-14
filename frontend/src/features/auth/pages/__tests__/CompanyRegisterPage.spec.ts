import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import CompanyRegisterPage from '../CompanyRegisterPage.vue'
import { createPinia, setActivePinia } from 'pinia'

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
      template: '<input :id="id" :placeholder="placeholder" />',
      props: ['id', 'modelValue', 'placeholder', 'invalid'],
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
    Select: {
      template: '<select :id="id"></select>',
      props: [
        'id',
        'modelValue',
        'options',
        'optionLabel',
        'optionValue',
        'placeholder',
        'invalid',
      ],
    },
    Button: {
      template: '<button :type="type">{{ label }}</button>',
      props: ['type', 'label', 'loading', 'icon', 'iconPos'],
    },
    Message: {
      template: '<div><slot /></div>',
      props: ['severity'],
    },
    Stepper: {
      template: '<div data-testid="stepper"><slot /></div>',
      props: ['value', 'linear'],
    },
    StepList: {
      template: '<div data-testid="step-list"><slot /></div>',
    },
    StepPanels: {
      template: '<div data-testid="step-panels"><slot /></div>',
    },
    Step: {
      template: '<div :data-step-value="value"><slot /></div>',
      props: ['value'],
    },
    StepPanel: {
      template: '<div :data-panel-value="value"><slot /></div>',
      props: ['value'],
    },
    CompanyInfoStep: {
      template:
        '<div data-testid="company-info-step"><input id="companyName" placeholder="Enter company name" /></div>',
      props: ['companyName', 'industry', 'size', 'country', 'submitted', 'errors', 'sizeOptions'],
    },
    AdminAccountStep: {
      template: '<div data-testid="admin-account-step"></div>',
      props: [
        'firstName',
        'lastName',
        'email',
        'password',
        'confirmPassword',
        'submitted',
        'errors',
        'loading',
      ],
    },
  },
}

describe('CompanyRegisterPage', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders step 1 (company info) initially', () => {
    const wrapper = shallowMount(CompanyRegisterPage, { global: globalConfig })

    expect(wrapper.text()).toContain('Register Your Company')
    expect(wrapper.text()).toContain('Company Info')
    expect(wrapper.text()).toContain('Admin Account')

    const companyInfoStep = wrapper.find('[data-testid="company-info-step"]')
    expect(companyInfoStep.exists()).toBe(true)
  })

  it('shows company name input on step 1', () => {
    const wrapper = shallowMount(CompanyRegisterPage, { global: globalConfig })

    const companyNameInput = wrapper.find('#companyName')
    expect(companyNameInput.exists()).toBe(true)
  })
})
