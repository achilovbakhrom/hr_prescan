# HR PreScan UI Redesign — Research (T2)

**Phase:** Research only. No spec, no tokens, no code. Await user reaction before T3.

**Taste anchors:** Arc, Raycast, Apple (visionOS / Tahoe / iOS 18). Calm, premium, confident. Not generic glassmorphism.

---

## 1. References

Each fetched live. Bullet form: what's good • anchor fit • transferable aspect.

### 1. Raycast — https://www.raycast.com/
- Semi-transparent overlay cards with backdrop blur over a deep navy/black field; vibrant blue/purple accents; floating keyboard glyph as a hero motif.
- **Anchor:** Raycast (exact), Apple (vibrancy treatment).
- **Transfer:** glass card pattern for dashboard widgets; command-palette density model for HR shortcuts (⌘K over candidates/vacancies); keyboard glyph as a landing hero device.

### 2. Arc Browser — https://arc.net/
- Minimalist whitespace, clean sectioning, calm staged-screenshot reveals; type hierarchy doing the heavy lifting.
- **Anchor:** Arc.
- **Transfer:** alternating full-width image/text sections for landing; calm restraint in marketing — don't over-animate. Arc's real signature (sidebar/spaces) is app-chrome — reference for our app-layout sidebar.

### 3. Linear — https://linear.app/
- Staged content reveals, status-badge language, subtle gradients behind layered cards, deliberate progression feel.
- **Anchor:** Raycast-adjacent premium SaaS.
- **Transfer:** status badge system (for vacancy lifecycle, candidate pipeline); horizontal timeline pattern (for interview schedules / pipeline stages).

### 4. Stripe — https://stripe.com/
- **Signature animated gradient "wave" shader** backgrounds; bold statement typography; parallax depth.
- **Anchor:** Apple (atmospheric backgrounds).
- **Transfer:** gradient-wave background as one of our 4 background variants; headline typography pattern for landing hero.

### 5. Apple Vision Pro — https://www.apple.com/apple-vision-pro/
- Spatial depth + layered translucent cards over atmospheric photography; floating cards with soft shadows; text at ~70–80% opacity with background blur for legibility.
- **Anchor:** Apple (exact — visionOS).
- **Transfer:** floating glass card over blurred background; translucent-overlay technique on imagery-rich sections (landing hero, public job detail); generous breathing room between sections.

### 6. Framer — https://framer.com/
- Dark mode primary, fluid motion vocabulary, modular self-contained feature cards.
- **Anchor:** Premium-SaaS-adjacent; motion reference.
- **Transfer:** modular feature-card composition; smooth enter animations for dashboard widgets.

### 7. Vercel — https://vercel.com/
- Neutral minimalism, multi-level nav cards with subtitles, hierarchical footer.
- **Anchor:** Arc-adjacent restraint.
- **Transfer:** nav card pattern for settings menus and admin; footer IA for landing.

**Not usable (blocked/403):** godly.website, land-book.com, openai.com, developer.apple.com/design/human-interface-guidelines/materials. I'll cite Apple HIG principles from general knowledge in T3 (vibrancy materials: `.thin`, `.regular`, `.thick`; 40–80% opacity bands).

---

## 2. Visual Direction Draft (≤8 bullets)

- **Core aesthetic:** "Calm vibrancy" — deep grounded surfaces, floating translucent glass panels, slow atmospheric motion behind sharp content. Apple visionOS vibe × Raycast's disciplined density.
- **Glass density & blur:** two-tier system. **Primary panels** (nav, dashboard cards): `backdrop-blur-2xl` with 6–8% white overlay in dark / 64–72% white in light, 1px soft-white border at 8–12% opacity. **Floating elements** (dialogs, popovers, toasts): `backdrop-blur-3xl`, slightly denser overlay, taller soft shadow. Glass never covers body text — body always on solid surface.
- **Background system philosophy:** 4 variants share a single "quiet envelope" baseline (deep near-black in dark, near-white in light) and differ only in the **mid-layer atmospheric animation**. One token swap changes vibe; contrast, legibility, and motion-budget stay constant.
- **Motion vocabulary:** easing `cubic-bezier(0.22, 1, 0.36, 1)` (iOS-style). Durations 240ms (micro), 420ms (card enter), 720ms (page transition). Animate on: page enter, data refresh, selection, focus. Do NOT animate on: scroll, hover of every element, or idle state. All motion respects `prefers-reduced-motion` via a `motion-safe:` utility layer — reduced mode disables transforms, keeps opacity fades only.
- **Type direction:** **Geist Sans** primary (Vercel — modern, crisp, designed for UI, free, variable weight) + **Geist Mono** for code/IDs/tokens. Alternate if we hate it: **General Sans** (slightly warmer). Geist wins because it reads like SF Pro without being SF Pro — matches our Apple anchor without licensing risk. Type scale reuses existing Tailwind.
- **Color accents:** existing `#0b0f17` dark bg and `#2563eb` accent stay. Add two new accents on top of the current palette: a **cool magenta/violet** (`~#7C5CFF`) for AI-origin moments (AI assistant, prescan result, interview AI voice) and a **warm peach** (`~#FF9B73`) reserved for celebratory states (offer sent, candidate passed). Rationale: Raycast-style dual-accent gives UI moments personality without polluting the neutral base.
- **What makes this different from generic glassmorphism:** generic glassmorphism puts glass everywhere and calls it a day. Ours uses glass as **a privileged material** — reserved for floating chrome and modal surfaces — while data and text live on solid, confident panels. Atmosphere lives in the *background* layer, not in every card.
- **Accessibility:** body text always on a solid surface (glass is chrome-only). Contrast ≥ 4.5:1 verified per token pair. Focus rings: 2px ring + 2px offset in accent color, always visible on glass. `prefers-reduced-motion: reduce` disables all transforms + particle animation; falls back to a soft static gradient; theme + background switch still work.

---

## 3. Four Background Variant Concepts

Shared baseline: quiet envelope (deep near-black dark / near-white light). All CSS/SVG — no WebGL. All respect `prefers-reduced-motion` by degrading to a static gradient.

1. **Aurora** — slow-drifting soft gradient ribbons (blurred conic gradients) animated via CSS `@keyframes` over 45–60s loops. Default variant. Reference: Stripe waves × visionOS atmosphere.
2. **Mesh** — an animated color-mesh gradient (4–6 blurred radial blobs, each with independent slow drift, blended via `mix-blend-mode: screen` in dark / `multiply` in light). Reference: Linear gradient layering.
3. **Constellation** — faint SVG points connected by hairline strokes, slow pulse + drift. Fits HR/AI/network semantic. Rendered on a single SVG + CSS; ≤40 nodes for perf. Reference: data-viz meets Apple Vision atmosphere.
4. **Vellum** — near-still, almost "off" mode — subtle noise texture + a single very slow breathing gradient. The "I just want to work" mode. Reference: Arc's restraint.

---

## 4. Three Logo Concepts

Semantics to keep: **AI + screening + trust**. Drop the literal shield; the new aesthetic already conveys trust through restraint. Candidates below — all monochrome-friendly, work at 16×16 favicon and 512×512 splash.

1. **Prism** — a minimal hexagonal prism / lens glyph. A single beam enters; 3 ranked beams exit, the top beam slightly brighter. Evokes "screening → ranked output." Works as a square mark or rotated 45° as a diamond.
2. **Signal** — a small waveform that resolves into a checkmark on the right third. Evokes interview (voice) + approval (pass). Animated hover variant: waveform completes the checkmark. Strong "AI voice" semantic for our LiveKit interview product.
3. **Nexus** — a compact node-graph glyph: 5 nodes, 4 connections, one node subtly highlighted (the "picked candidate"). Modern AI-company aesthetic, scales down cleanly.

User picks one at T4. I'll spec it fully in T3 with exact SVG construction + favicon + dark/light variants.

---

## 5. Dependency Proposals

| Package | Size (gz) | Reason | Verdict |
|---|---|---|---|
| `motion-v` | ~8 kB | Composable Vue 3 animation primitives; declarative, tree-shakable; best-in-class ergonomics for Vue. Covers page transitions, card enter, list stagger. | **Recommend** |
| `@vueuse/motion` | ~6 kB | Viable alternative to motion-v. Slightly less ergonomic API. | Skip unless we already use VueUse heavily (and we do — but motion-v has a cleaner API) |
| `@tsparticles/vue3` | ~30+ kB | Particle engine. **Skip** — we can do Constellation + Aurora in CSS/SVG at zero JS cost. |
| GSAP | ~25 kB | Heavy. Skip. |
| Lottie | ~60 kB | Heavy. Skip — we don't need After Effects-grade motion. |
| Inter / Geist fonts | self-hosted | `@fontsource/geist-sans` + `@fontsource/geist-mono`. Subset to Latin, `font-display: swap`. Estimated ~40 kB total after subsetting. | **Recommend** |

**Net new JS cost: ~8 kB gz** (motion-v only).
**Net new font cost: ~40 kB** (subsetted, cached after first paint).

---

## 6. Handoff to User

You have 4 decisions to make before T3:

1. **Approve the 7 references** — or redirect ("less Raycast, more Apple" / "drop Stripe" / "add X").
2. **Approve visual direction** — or push back on any of the 8 bullets.
3. **Pick 1 of 3 logo concepts** — Prism / Signal / Nexus. (Or say "none, iterate.")
4. **Approve motion-v + Geist fonts**, or propose alternatives.

After your answers, I run T3 (full spec: tokens, typography scale, PrimeVue overrides, per-page component specs, background variant specs, logo SVG spec). No code until then.
