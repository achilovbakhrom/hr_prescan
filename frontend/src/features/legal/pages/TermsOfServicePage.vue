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
        <h1 class="text-3xl font-bold text-gray-900">Terms of Service</h1>
        <p class="mt-2 text-sm text-gray-500">Last updated: January 1, 2025</p>
      </div>
    </div>

    <!-- Content -->
    <div class="mx-auto max-w-4xl px-6 py-12">
      <div class="space-y-10 rounded-2xl bg-white p-10 shadow-sm">
        <section>
          <h2 class="mb-4 text-xl font-semibold text-gray-900">1. Acceptance of Terms</h2>
          <p class="leading-relaxed text-gray-600">
            By accessing or using the PreScreen AI platform ("Service"), you agree to be bound by
            these Terms of Service ("Terms"). If you do not agree to these Terms, please do not use
            the Service. These Terms apply to all users, including HR professionals, company
            administrators, and job candidates.
          </p>
        </section>

        <section>
          <h2 class="mb-4 text-xl font-semibold text-gray-900">2. Description of Service</h2>
          <p class="leading-relaxed text-gray-600">
            PreScreen AI provides an AI-powered candidate pre-screening platform that enables
            companies to conduct automated video interviews, score candidates, and manage hiring
            workflows. The Service includes web application access, AI interview capabilities,
            reporting tools, and related features as described in your subscription plan.
          </p>
        </section>

        <section>
          <h2 class="mb-4 text-xl font-semibold text-gray-900">3. Account Registration</h2>
          <p class="leading-relaxed text-gray-600">
            To use the Service, you must register for an account and provide accurate, complete, and
            current information. You are responsible for maintaining the confidentiality of your
            account credentials and for all activities that occur under your account. Notify us
            immediately of any unauthorized use of your account at
            <a href="mailto:security@hrprescan.com" class="text-blue-600 hover:underline"
              >security@hrprescan.com</a
            >.
          </p>
        </section>

        <section>
          <h2 class="mb-4 text-xl font-semibold text-gray-900">4. Acceptable Use</h2>
          <p class="mb-3 leading-relaxed text-gray-600">You agree not to use the Service to:</p>
          <ul class="list-inside list-disc space-y-2 text-gray-600">
            <li>Violate any applicable laws or regulations</li>
            <li>Discriminate against candidates based on protected characteristics</li>
            <li>Upload malicious code or attempt to breach the platform's security</li>
            <li>Collect or harvest data from other users without consent</li>
            <li>Misrepresent your identity or affiliation</li>
            <li>Use the Service for purposes other than legitimate hiring activities</li>
          </ul>
        </section>

        <section>
          <h2 class="mb-4 text-xl font-semibold text-gray-900">5. Subscriptions and Payment</h2>
          <p class="leading-relaxed text-gray-600">
            Access to premium features requires a paid subscription. Fees are charged in advance on
            a monthly or annual basis. All fees are non-refundable except as expressly stated in our
            Refund Policy. We reserve the right to modify pricing with 30 days' notice. Failure to
            pay may result in suspension or termination of your account.
          </p>
        </section>

        <section>
          <h2 class="mb-4 text-xl font-semibold text-gray-900">6. Intellectual Property</h2>
          <p class="leading-relaxed text-gray-600">
            The Service, including its software, design, and content, is owned by PreScreen AI and
            protected by intellectual property laws. You are granted a limited, non-exclusive,
            non-transferable license to use the Service for your internal business purposes. You
            retain ownership of any content you upload, and grant us a license to process it solely
            to provide the Service.
          </p>
        </section>

        <section>
          <h2 class="mb-4 text-xl font-semibold text-gray-900">7. AI-Generated Assessments</h2>
          <p class="leading-relaxed text-gray-600">
            AI-generated scores, transcripts, and assessments are provided as informational tools to
            assist your hiring process. They do not constitute employment decisions. You remain
            solely responsible for all hiring decisions and must ensure compliance with applicable
            employment and anti-discrimination laws. PreScreen AI disclaims liability for hiring
            decisions made based on AI outputs.
          </p>
        </section>

        <section>
          <h2 class="mb-4 text-xl font-semibold text-gray-900">8. Limitation of Liability</h2>
          <p class="leading-relaxed text-gray-600">
            To the maximum extent permitted by law, PreScreen AI shall not be liable for any
            indirect, incidental, special, consequential, or punitive damages, including loss of
            profits or data, arising from your use of the Service. Our total liability shall not
            exceed the amounts paid by you in the 12 months preceding the claim.
          </p>
        </section>

        <section>
          <h2 class="mb-4 text-xl font-semibold text-gray-900">9. Termination</h2>
          <p class="leading-relaxed text-gray-600">
            We may suspend or terminate your account at any time for violation of these Terms or for
            any other reason with reasonable notice. You may terminate your account at any time by
            contacting us. Upon termination, your right to use the Service ceases and we may delete
            your data in accordance with our Privacy Policy.
          </p>
        </section>

        <section>
          <h2 class="mb-4 text-xl font-semibold text-gray-900">10. Governing Law</h2>
          <p class="leading-relaxed text-gray-600">
            These Terms are governed by and construed in accordance with applicable law. Any
            disputes shall be resolved through binding arbitration or in courts of competent
            jurisdiction. If any provision of these Terms is found invalid, the remaining provisions
            will continue in effect.
          </p>
        </section>

        <section>
          <h2 class="mb-4 text-xl font-semibold text-gray-900">11. Contact</h2>
          <p class="leading-relaxed text-gray-600">
            For questions about these Terms, contact us at:
          </p>
          <div class="mt-3 text-gray-600">
            <p>PreScreen AI</p>
            <p>
              Email:
              <a href="mailto:legal@hrprescan.com" class="text-blue-600 hover:underline"
                >legal@hrprescan.com</a
              >
            </p>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>
