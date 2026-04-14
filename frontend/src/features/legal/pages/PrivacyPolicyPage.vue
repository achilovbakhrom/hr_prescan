<script setup lang="ts">
import { useRouter } from 'vue-router'
import Button from 'primevue/button'

const router = useRouter()

function goBack(): void {
  router.back()
}
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="border-b border-gray-200 bg-white">
      <div class="mx-auto max-w-4xl px-6 py-6">
        <Button
          label="Back"
          icon="pi pi-arrow-left"
          text
          severity="secondary"
          class="mb-4"
          @click="goBack"
        />
        <h1 class="text-3xl font-bold text-gray-900">Privacy Policy</h1>
        <p class="mt-2 text-sm text-gray-500">Last updated: January 1, 2025</p>
      </div>
    </div>

    <!-- Content -->
    <div class="mx-auto max-w-4xl px-6 py-12">
      <div class="space-y-10 rounded-2xl bg-white p-10 shadow-sm">
        <section>
          <h2 class="mb-4 text-xl font-semibold text-gray-900">1. Introduction</h2>
          <p class="leading-relaxed text-gray-600">
            PreScreen AI ("we", "our", or "us") is committed to protecting your personal
            information. This Privacy Policy explains how we collect, use, disclose, and safeguard
            your information when you use our AI-powered candidate pre-screening platform.
          </p>
        </section>

        <section>
          <h2 class="mb-4 text-xl font-semibold text-gray-900">2. Information We Collect</h2>
          <p class="mb-3 leading-relaxed text-gray-600">
            We collect information you provide directly to us, including:
          </p>
          <ul class="list-inside list-disc space-y-2 text-gray-600">
            <li>Account registration data (name, email, company name)</li>
            <li>Candidate profile information (resume, work history, skills)</li>
            <li>Video interview recordings and transcripts</li>
            <li>Usage data and platform interactions</li>
            <li>Payment information (processed securely via third-party providers)</li>
          </ul>
        </section>

        <section>
          <h2 class="mb-4 text-xl font-semibold text-gray-900">3. How We Use Your Information</h2>
          <p class="mb-3 leading-relaxed text-gray-600">We use the information we collect to:</p>
          <ul class="list-inside list-disc space-y-2 text-gray-600">
            <li>Provide, operate, and maintain our platform</li>
            <li>Process AI-powered interview analysis and scoring</li>
            <li>Send transactional emails and notifications</li>
            <li>Improve and personalize your experience</li>
            <li>Comply with legal obligations</li>
          </ul>
        </section>

        <section>
          <h2 class="mb-4 text-xl font-semibold text-gray-900">4. Data Retention</h2>
          <p class="leading-relaxed text-gray-600">
            We retain your personal data for as long as your account is active or as needed to
            provide our services. Candidate data (including video recordings) is retained for 12
            months after an application is closed, unless you request earlier deletion. You may
            request deletion of your data at any time by contacting us at
            <a href="mailto:privacy@hrprescan.com" class="text-blue-600 hover:underline"
              >privacy@hrprescan.com</a
            >.
          </p>
        </section>

        <section>
          <h2 class="mb-4 text-xl font-semibold text-gray-900">5. Sharing of Information</h2>
          <p class="leading-relaxed text-gray-600">
            We do not sell your personal information. We may share your information with trusted
            third-party service providers (such as cloud hosting, payment processing, and AI
            infrastructure) who assist us in operating the platform, subject to confidentiality
            agreements. We may also disclose information when required by law.
          </p>
        </section>

        <section>
          <h2 class="mb-4 text-xl font-semibold text-gray-900">6. Cookies</h2>
          <p class="leading-relaxed text-gray-600">
            We use cookies and similar tracking technologies to analyze usage, remember preferences,
            and improve our service. You may control cookie settings through your browser or via our
            cookie consent banner. See our Cookie Policy for more details.
          </p>
        </section>

        <section>
          <h2 class="mb-4 text-xl font-semibold text-gray-900">7. Your Rights (GDPR)</h2>
          <p class="mb-3 leading-relaxed text-gray-600">
            If you are located in the European Economic Area, you have the following rights
            regarding your personal data:
          </p>
          <ul class="list-inside list-disc space-y-2 text-gray-600">
            <li>Right of access to your personal data</li>
            <li>Right to rectification of inaccurate data</li>
            <li>Right to erasure ("right to be forgotten")</li>
            <li>Right to restriction of processing</li>
            <li>Right to data portability</li>
            <li>Right to object to processing</li>
          </ul>
          <p class="mt-3 leading-relaxed text-gray-600">
            To exercise any of these rights, contact us at
            <a href="mailto:privacy@hrprescan.com" class="text-blue-600 hover:underline"
              >privacy@hrprescan.com</a
            >.
          </p>
        </section>

        <section>
          <h2 class="mb-4 text-xl font-semibold text-gray-900">8. Security</h2>
          <p class="leading-relaxed text-gray-600">
            We implement industry-standard security measures including encryption at rest and in
            transit, access controls, and regular security audits. However, no method of
            transmission over the Internet is 100% secure, and we cannot guarantee absolute
            security.
          </p>
        </section>

        <section>
          <h2 class="mb-4 text-xl font-semibold text-gray-900">9. Contact Us</h2>
          <p class="leading-relaxed text-gray-600">
            If you have questions about this Privacy Policy or our data practices, please contact us
            at:
          </p>
          <div class="mt-3 text-gray-600">
            <p>PreScreen AI</p>
            <p>
              Email:
              <a href="mailto:privacy@hrprescan.com" class="text-blue-600 hover:underline"
                >privacy@hrprescan.com</a
              >
            </p>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>
