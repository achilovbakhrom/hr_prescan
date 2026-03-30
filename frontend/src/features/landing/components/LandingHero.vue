<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import Button from 'primevue/button'
import { ROUTE_NAMES } from '@/shared/constants/routes'

const router = useRouter()
const { t } = useI18n()

// Animated chat demo messages
interface DemoMessage {
  role: 'ai' | 'candidate'
  text: string
}

const visibleMessages = ref<DemoMessage[]>([])
const chatDemoComplete = ref(false)

const demoMessages: DemoMessage[] = [
  { role: 'ai', text: '👋 Hi! I\'m the AI interviewer for the Senior Frontend Developer role at TechCorp. Ready to begin?' },
  { role: 'candidate', text: 'Yes, let\'s go!' },
  { role: 'ai', text: 'Tell me about a complex UI challenge you solved recently.' },
  { role: 'candidate', text: 'I built a real-time collaborative editor with conflict resolution using CRDTs and Vue 3.' },
  { role: 'ai', text: '🎯 Impressive! Technical Skills: 9/10 • Communication: 8/10 • Advancing to interview stage.' },
]

onMounted(() => {
  let i = 0
  const interval = setInterval(() => {
    if (i < demoMessages.length) {
      visibleMessages.value.push(demoMessages[i])
      i++
    } else {
      chatDemoComplete.value = true
      clearInterval(interval)
    }
  }, 1200)
})
</script>

<template>
  <section class="relative overflow-hidden px-6 py-20 sm:py-28 lg:py-36">
    <!-- Background gradient -->
    <div class="absolute inset-0 bg-gradient-to-br from-slate-50 via-blue-50/40 to-indigo-50/60"></div>
    <!-- Animated floating shapes -->
    <div class="absolute -top-32 right-1/4 h-[500px] w-[500px] rounded-full bg-blue-200/20 blur-3xl animate-float"></div>
    <div class="absolute -bottom-32 left-1/4 h-[400px] w-[400px] rounded-full bg-indigo-200/20 blur-3xl animate-float-delayed"></div>

    <div class="relative mx-auto max-w-6xl">
      <div class="grid items-center gap-12 lg:grid-cols-2 lg:gap-16">
        <!-- Left: Text content -->
        <div class="text-center lg:text-left">
          <!-- Badge -->
          <div class="scroll-animate mb-6 inline-flex items-center gap-2 rounded-full border border-blue-200/60 bg-blue-50/80 px-4 py-1.5 text-sm font-medium text-blue-700 backdrop-blur-sm">
            <i class="pi pi-sparkles text-xs"></i> {{ t('landing.badge.poweredBy') }}
          </div>

          <!-- Headline -->
          <h1 class="scroll-animate mb-5 text-3xl font-extrabold tracking-tight text-gray-900 sm:text-4xl lg:text-5xl xl:text-6xl">
            {{ t('landing.hero.title') }}
          </h1>

          <!-- Subtitle -->
          <p class="scroll-animate mb-8 max-w-lg text-base leading-relaxed text-gray-500 sm:text-lg lg:mx-0 mx-auto">
            {{ t('landing.hero.subtitle') }}
          </p>

          <!-- CTAs -->
          <div class="scroll-animate flex flex-col items-center gap-3 sm:flex-row lg:justify-start justify-center">
            <Button
              :label="t('landing.hero.cta')"
              icon="pi pi-arrow-right"
              icon-pos="right"
              size="large"
              class="w-full sm:w-auto"
              @click="router.push({ name: ROUTE_NAMES.REGISTER })"
            />
            <Button
              :label="t('landing.hero.browseJobs')"
              icon="pi pi-search"
              severity="secondary"
              outlined
              size="large"
              class="w-full sm:w-auto"
              @click="router.push({ name: ROUTE_NAMES.JOB_BOARD })"
            />
          </div>

          <!-- Trust signals -->
          <p class="scroll-animate mt-4 text-sm text-gray-400">
            {{ t('landing.promo.noCreditCard') }} &middot; {{ t('landing.promo.freeTrial') }}
          </p>
        </div>

        <!-- Right: Animated chat demo -->
        <div class="scroll-animate scroll-animate-delay-2 hidden sm:block">
          <div class="relative rounded-2xl border border-gray-200/60 bg-white/90 shadow-2xl shadow-blue-900/10 backdrop-blur-sm">
            <!-- Chat header -->
            <div class="flex items-center gap-3 rounded-t-2xl border-b border-gray-100 bg-gradient-to-r from-blue-600 to-indigo-600 px-5 py-3.5">
              <div class="flex h-8 w-8 items-center justify-center rounded-full bg-white/20">
                <i class="pi pi-comments text-sm text-white"></i>
              </div>
              <div>
                <p class="text-sm font-semibold text-white">{{ t('interviews.chat.aiPrescanning') }}</p>
                <div class="flex items-center gap-1.5">
                  <span class="h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
                  <span class="text-xs text-blue-100">{{ t('interviews.chat.online') }}</span>
                </div>
              </div>
            </div>

            <!-- Chat messages -->
            <div class="h-[320px] space-y-3 overflow-hidden p-5">
              <TransitionGroup
                name="chat-message"
                tag="div"
                class="space-y-3"
              >
                <div
                  v-for="(msg, idx) in visibleMessages"
                  :key="idx"
                  class="flex"
                  :class="msg.role === 'candidate' ? 'justify-end' : 'justify-start'"
                >
                  <!-- AI message -->
                  <div
                    v-if="msg.role === 'ai'"
                    class="flex max-w-[80%] gap-2"
                  >
                    <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-blue-100">
                      <i class="pi pi-sparkles text-[10px] text-blue-600"></i>
                    </div>
                    <div class="rounded-2xl rounded-tl-sm bg-gray-100 px-4 py-2.5">
                      <p class="text-sm text-gray-700">{{ msg.text }}</p>
                    </div>
                  </div>

                  <!-- Candidate message -->
                  <div
                    v-else
                    class="max-w-[75%]"
                  >
                    <div class="rounded-2xl rounded-tr-sm bg-blue-600 px-4 py-2.5">
                      <p class="text-sm text-white">{{ msg.text }}</p>
                    </div>
                  </div>
                </div>
              </TransitionGroup>

              <!-- Typing indicator -->
              <div
                v-if="visibleMessages.length > 0 && !chatDemoComplete"
                class="flex items-center gap-2"
              >
                <div class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-blue-100">
                  <i class="pi pi-sparkles text-[10px] text-blue-600"></i>
                </div>
                <div class="flex gap-1 rounded-2xl bg-gray-100 px-4 py-3">
                  <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-400" style="animation-delay: 0ms"></span>
                  <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-400" style="animation-delay: 150ms"></span>
                  <span class="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-400" style="animation-delay: 300ms"></span>
                </div>
              </div>
            </div>

            <!-- Chat input mockup -->
            <div class="flex items-center gap-2 border-t border-gray-100 px-5 py-3">
              <div class="flex-1 rounded-full bg-gray-50 px-4 py-2.5">
                <span class="text-sm text-gray-400">{{ t('interviews.chat.typeYourAnswer') }}</span>
              </div>
              <div class="flex h-9 w-9 items-center justify-center rounded-full bg-blue-600">
                <i class="pi pi-send text-xs text-white"></i>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.chat-message-enter-active {
  transition: all 0.4s ease;
}
.chat-message-enter-from {
  opacity: 0;
  transform: translateY(12px);
}
</style>
