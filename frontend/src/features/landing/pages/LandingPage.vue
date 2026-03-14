<script setup lang="ts">
import { useRouter } from 'vue-router'
import Button from 'primevue/button'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const router = useRouter()

function goToRegister(): void {
  router.push({ name: ROUTE_NAMES.REGISTER })
}

function goToLogin(): void {
  router.push({ name: ROUTE_NAMES.LOGIN })
}

function goToPricing(): void {
  router.push({ name: ROUTE_NAMES.PRICING })
}

interface Feature {
  icon: string
  title: string
  description: string
}

interface Step {
  number: string
  title: string
  description: string
}

const features: Feature[] = [
  {
    icon: 'pi pi-microphone',
    title: 'AI-Powered Interviews',
    description:
      'Automated video interviews conducted by an AI voice agent, available 24/7 for candidates worldwide.',
  },
  {
    icon: 'pi pi-chart-bar',
    title: 'Smart Scoring',
    description:
      'Objective candidate evaluation with AI-generated scores, transcripts, and detailed performance insights.',
  },
  {
    icon: 'pi pi-shield',
    title: 'Anti-Cheating Protection',
    description:
      'Real-time proctoring with face detection and environment monitoring ensures interview integrity.',
  },
  {
    icon: 'pi pi-briefcase',
    title: 'Easy Management',
    description:
      'Manage vacancies, track candidates, schedule interviews, and collaborate with your team in one platform.',
  },
]

const steps: Step[] = [
  {
    number: '01',
    title: 'Post a Vacancy',
    description:
      'Create a job listing with a custom questionnaire. Share the public link with candidates anywhere.',
  },
  {
    number: '02',
    title: 'Candidates Apply',
    description:
      'Candidates submit applications and schedule AI video interviews at their convenience.',
  },
  {
    number: '03',
    title: 'Review AI Results',
    description:
      'Receive scored transcripts, video recordings, and AI insights to make faster hiring decisions.',
  },
]
</script>

<template>
  <div class="min-h-screen bg-white">
    <!-- Navigation -->
    <nav
      class="sticky top-0 z-50 border-b border-gray-100 bg-white/90 backdrop-blur-sm"
    >
      <div
        class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4"
      >
        <div class="flex items-center gap-2">
          <div
            class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600"
          >
            <i class="pi pi-bolt text-sm text-white"></i>
          </div>
          <span class="text-xl font-bold text-gray-900">HR PreScan</span>
        </div>
        <div class="hidden items-center gap-6 md:flex">
          <a
            href="#features"
            class="text-sm font-medium text-gray-600 transition-colors hover:text-gray-900"
            >Features</a
          >
          <a
            href="#how-it-works"
            class="text-sm font-medium text-gray-600 transition-colors hover:text-gray-900"
            >How It Works</a
          >
          <a
            href="#pricing"
            class="text-sm font-medium text-gray-600 transition-colors hover:text-gray-900"
            >Pricing</a
          >
        </div>
        <div class="flex items-center gap-3">
          <Button
            label="Sign In"
            text
            severity="secondary"
            class="hidden sm:flex"
            @click="goToLogin"
          />
          <Button label="Get Started Free" @click="goToRegister" />
        </div>
      </div>
    </nav>

    <!-- Hero Section -->
    <section
      class="relative overflow-hidden bg-gradient-to-br from-blue-50 via-white to-indigo-50 px-6 py-24 sm:py-32"
    >
      <div class="absolute inset-0 overflow-hidden">
        <div
          class="absolute -top-40 right-0 h-80 w-80 rounded-full bg-blue-100 opacity-40 blur-3xl"
        ></div>
        <div
          class="absolute -bottom-40 left-0 h-80 w-80 rounded-full bg-indigo-100 opacity-40 blur-3xl"
        ></div>
      </div>
      <div class="relative mx-auto max-w-4xl text-center">
        <span
          class="mb-6 inline-flex items-center gap-2 rounded-full bg-blue-100 px-4 py-1.5 text-sm font-medium text-blue-700"
        >
          <i class="pi pi-bolt text-xs"></i>
          Powered by Advanced AI
        </span>
        <h1
          class="mb-6 text-5xl font-extrabold tracking-tight text-gray-900 sm:text-6xl lg:text-7xl"
        >
          AI-Powered Candidate
          <span class="text-blue-600"> Pre-Screening</span>
        </h1>
        <p class="mx-auto mb-10 max-w-2xl text-xl leading-relaxed text-gray-600">
          Screen hundreds of candidates automatically with AI video interviews.
          Save time, reduce bias, and hire the best talent faster than ever
          before.
        </p>
        <div class="flex flex-col items-center justify-center gap-4 sm:flex-row">
          <Button
            label="Start Free Trial"
            icon="pi pi-arrow-right"
            icon-pos="right"
            size="large"
            class="w-full sm:w-auto"
            @click="goToRegister"
          />
          <Button
            label="Watch Demo"
            icon="pi pi-play"
            text
            severity="secondary"
            size="large"
            class="w-full sm:w-auto"
          />
        </div>
        <p class="mt-4 text-sm text-gray-500">
          No credit card required · 14-day free trial · Cancel anytime
        </p>
      </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="px-6 py-24">
      <div class="mx-auto max-w-7xl">
        <div class="mb-16 text-center">
          <h2 class="mb-4 text-4xl font-bold text-gray-900">
            Everything you need to hire smarter
          </h2>
          <p class="mx-auto max-w-2xl text-lg text-gray-600">
            Our AI platform handles the entire pre-screening process so your HR
            team can focus on what matters most — finding the right people.
          </p>
        </div>
        <div class="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div
            v-for="feature in features"
            :key="feature.title"
            class="group rounded-2xl border border-gray-100 bg-white p-8 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-lg"
          >
            <div
              class="mb-5 flex h-14 w-14 items-center justify-center rounded-xl bg-blue-50 text-blue-600 transition-colors group-hover:bg-blue-600 group-hover:text-white"
            >
              <i :class="feature.icon" class="text-2xl"></i>
            </div>
            <h3 class="mb-3 text-xl font-semibold text-gray-900">
              {{ feature.title }}
            </h3>
            <p class="leading-relaxed text-gray-600">
              {{ feature.description }}
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section id="how-it-works" class="bg-gray-50 px-6 py-24">
      <div class="mx-auto max-w-7xl">
        <div class="mb-16 text-center">
          <h2 class="mb-4 text-4xl font-bold text-gray-900">How It Works</h2>
          <p class="mx-auto max-w-xl text-lg text-gray-600">
            Get up and running in minutes. Our streamlined process makes
            AI-powered hiring effortless.
          </p>
        </div>
        <div class="relative grid gap-8 lg:grid-cols-3">
          <!-- Connecting line -->
          <div
            class="absolute left-1/6 right-1/6 top-8 hidden h-0.5 bg-blue-200 lg:block"
          ></div>
          <div
            v-for="step in steps"
            :key="step.number"
            class="relative flex flex-col items-center text-center"
          >
            <div
              class="relative z-10 mb-6 flex h-16 w-16 items-center justify-center rounded-full bg-blue-600 text-2xl font-bold text-white shadow-lg"
            >
              {{ step.number }}
            </div>
            <h3 class="mb-3 text-xl font-semibold text-gray-900">
              {{ step.title }}
            </h3>
            <p class="leading-relaxed text-gray-600">{{ step.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="px-6 py-24">
      <div class="mx-auto max-w-7xl">
        <div class="grid gap-8 text-center sm:grid-cols-3">
          <div>
            <div class="text-5xl font-extrabold text-blue-600">10x</div>
            <div class="mt-2 text-lg font-medium text-gray-700">
              Faster Screening
            </div>
            <div class="mt-1 text-sm text-gray-500">
              Compared to manual interviews
            </div>
          </div>
          <div>
            <div class="text-5xl font-extrabold text-blue-600">90%</div>
            <div class="mt-2 text-lg font-medium text-gray-700">
              Time Saved
            </div>
            <div class="mt-1 text-sm text-gray-500">In the hiring process</div>
          </div>
          <div>
            <div class="text-5xl font-extrabold text-blue-600">24/7</div>
            <div class="mt-2 text-lg font-medium text-gray-700">
              Available
            </div>
            <div class="mt-1 text-sm text-gray-500">
              Candidates interview anytime
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Pricing CTA Section -->
    <section id="pricing" class="bg-blue-600 px-6 py-24">
      <div class="mx-auto max-w-4xl text-center">
        <h2 class="mb-6 text-4xl font-bold text-white">
          Ready to transform your hiring?
        </h2>
        <p class="mx-auto mb-10 max-w-xl text-xl text-blue-100">
          Join companies already using HR PreScan to find top talent faster.
          Start your free 14-day trial today.
        </p>
        <div class="flex flex-col items-center justify-center gap-4 sm:flex-row">
          <Button
            label="Start Free Trial"
            icon="pi pi-arrow-right"
            icon-pos="right"
            size="large"
            severity="contrast"
            class="w-full sm:w-auto"
            @click="goToRegister"
          />
          <Button
            label="View Pricing Plans"
            text
            class="w-full text-white sm:w-auto hover:text-blue-100"
            size="large"
            @click="goToPricing"
          />
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="border-t border-gray-200 bg-gray-900 px-6 py-16">
      <div class="mx-auto max-w-7xl">
        <div class="grid gap-12 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <div class="mb-4 flex items-center gap-2">
              <div
                class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600"
              >
                <i class="pi pi-bolt text-sm text-white"></i>
              </div>
              <span class="text-xl font-bold text-white">HR PreScan</span>
            </div>
            <p class="text-sm leading-relaxed text-gray-400">
              AI-powered candidate pre-screening that helps companies hire
              faster and smarter.
            </p>
          </div>
          <div>
            <h4 class="mb-4 text-sm font-semibold uppercase tracking-wider text-gray-300">
              Product
            </h4>
            <ul class="space-y-2">
              <li>
                <a
                  href="#features"
                  class="text-sm text-gray-400 transition-colors hover:text-white"
                  >Features</a
                >
              </li>
              <li>
                <a
                  href="#how-it-works"
                  class="text-sm text-gray-400 transition-colors hover:text-white"
                  >How It Works</a
                >
              </li>
              <li>
                <RouterLink
                  to="/pricing"
                  class="text-sm text-gray-400 transition-colors hover:text-white"
                  >Pricing</RouterLink
                >
              </li>
            </ul>
          </div>
          <div>
            <h4 class="mb-4 text-sm font-semibold uppercase tracking-wider text-gray-300">
              Company
            </h4>
            <ul class="space-y-2">
              <li>
                <RouterLink
                  to="/privacy"
                  class="text-sm text-gray-400 transition-colors hover:text-white"
                  >Privacy Policy</RouterLink
                >
              </li>
              <li>
                <RouterLink
                  to="/terms"
                  class="text-sm text-gray-400 transition-colors hover:text-white"
                  >Terms of Service</RouterLink
                >
              </li>
            </ul>
          </div>
          <div>
            <h4 class="mb-4 text-sm font-semibold uppercase tracking-wider text-gray-300">
              Get Started
            </h4>
            <ul class="space-y-2">
              <li>
                <RouterLink
                  to="/login"
                  class="text-sm text-gray-400 transition-colors hover:text-white"
                  >Sign In</RouterLink
                >
              </li>
              <li>
                <RouterLink
                  to="/register"
                  class="text-sm text-gray-400 transition-colors hover:text-white"
                  >Create Account</RouterLink
                >
              </li>
            </ul>
          </div>
        </div>
        <div
          class="mt-12 border-t border-gray-800 pt-8 text-center text-sm text-gray-500"
        >
          &copy; {{ new Date().getFullYear() }} HR PreScan. All rights reserved.
        </div>
      </div>
    </footer>
  </div>
</template>
