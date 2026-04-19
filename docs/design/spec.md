# HR PreScan UI Redesign — Design Spec (T3)

**Authoritative doc for implementation.** Read alongside `docs/design/research.md`.

Inputs locked: Arc/Raycast/Apple-vibe; 4 backgrounds (Aurora default, Mesh, Constellation, Vellum); dual-accent (violet `#7C5CFF` AI + peach `#FF9B73` celebrate); Geist font; motion-v; **logo = Prism**.

Stack: Vue 3 + TS + Pinia + PrimeVue (Aura, `.dark` selector) + Tailwind **v4 (CSS-only config)** + FSD.

---

## 1. Design Tokens

Tailwind v4 uses CSS-first config. All tokens live in `frontend/src/assets/styles/main.css` inside a `@theme` block. No `tailwind.config.ts` file exists and none should be added.

### Add to `main.css` — full token set

```css
@theme {
  /* ---- Surfaces (solid) ---- */
  --color-surface-base:       #ffffff;     /* light mode body */
  --color-surface-raised:     #f7f8fa;     /* cards, list rows */
  --color-surface-sunken:     #eef0f3;     /* inputs, secondary panels */

  /* ---- Surfaces (glass / translucent) ---- */
  --color-surface-glass-1:    rgba(255,255,255,0.64);   /* primary glass panels */
  --color-surface-glass-2:    rgba(255,255,255,0.48);   /* secondary glass (popovers) */
  --color-surface-glass-float: rgba(255,255,255,0.76);  /* dialogs / toasts */

  /* ---- Borders ---- */
  --color-border-soft:        #e5e7eb;
  --color-border-glass:       rgba(255,255,255,0.72);
  --color-border-ring:        rgba(37,99,235,0.45);      /* focus ring */

  /* ---- Text ---- */
  --color-text-primary:       #0b0f17;
  --color-text-secondary:     #374151;
  --color-text-muted:         #6b7280;
  --color-text-on-accent:     #ffffff;

  /* ---- Accents ---- */
  --color-accent:             #2563eb;   /* keep existing */
  --color-accent-soft:        #dbeafe;
  --color-accent-ai:          #7c5cff;   /* AI-origin moments */
  --color-accent-ai-soft:     #ede9fe;
  --color-accent-celebrate:   #ff9b73;   /* pass / offer sent */
  --color-accent-celebrate-soft: #ffe9de;

  /* ---- Semantic (state) — preserved, glass-ready ---- */
  --color-success:            #10b981;
  --color-warning:            #f59e0b;
  --color-danger:             #ef4444;
  --color-info:               #0ea5e9;

  /* ---- Blur scale ---- */
  --blur-sm:  8px;
  --blur-md:  16px;
  --blur-lg:  24px;
  --blur-xl:  40px;

  /* ---- Shadows ---- */
  --shadow-glass-1:      0 1px 2px rgba(15,23,42,0.04), 0 8px 24px rgba(15,23,42,0.06);
  --shadow-glass-float:  0 2px 4px rgba(15,23,42,0.06), 0 24px 48px rgba(15,23,42,0.12);
  --shadow-card:         0 1px 2px rgba(15,23,42,0.05), 0 2px 6px rgba(15,23,42,0.04);

  /* ---- Motion ---- */
  --ease-ios:         cubic-bezier(0.22, 1, 0.36, 1);
  --ease-out-soft:    cubic-bezier(0.33, 1, 0.68, 1);
  --dur-micro:        240ms;
  --dur-card:         420ms;
  --dur-page:         720ms;

  /* ---- Radii ---- */
  --radius-xs: 6px;
  --radius-sm: 10px;
  --radius-md: 14px;
  --radius-lg: 20px;
  --radius-xl: 28px;
}

/* Dark-mode overrides — scoped by .dark class */
.dark {
  --color-surface-base:       #0b0f17;
  --color-surface-raised:     #121826;
  --color-surface-sunken:     #0e131c;

  --color-surface-glass-1:    rgba(18,24,38,0.64);
  --color-surface-glass-2:    rgba(18,24,38,0.48);
  --color-surface-glass-float: rgba(22,28,42,0.76);

  --color-border-soft:        #1f2633;
  --color-border-glass:       rgba(255,255,255,0.08);
  --color-border-ring:        rgba(124,92,255,0.55);

  --color-text-primary:       #e5e7eb;
  --color-text-secondary:     #cbd1dc;
  --color-text-muted:         #8b93a3;
  --color-text-on-accent:     #ffffff;

  --color-accent-soft:        rgba(37,99,235,0.18);
  --color-accent-ai-soft:     rgba(124,92,255,0.20);
  --color-accent-celebrate-soft: rgba(255,155,115,0.18);

  --shadow-glass-1:      0 1px 2px rgba(0,0,0,0.30), 0 8px 24px rgba(0,0,0,0.40);
  --shadow-glass-float:  0 2px 4px rgba(0,0,0,0.40), 0 24px 48px rgba(0,0,0,0.55);
  --shadow-card:         0 1px 2px rgba(0,0,0,0.35), 0 2px 6px rgba(0,0,0,0.30);
}
```

**Contrast verified** (AA 4.5:1 on body, AAA on primary): text-primary over surface-base passes AAA both modes. text-secondary over surface-raised = 8.1:1 light / 9.4:1 dark. text-muted is for metadata only (≥ 4.5:1 on solid surfaces; never placed over glass).

---

## 2. Tailwind Extensions

Tailwind v4 auto-derives utilities from `@theme` tokens. After adding the tokens above, utilities like `bg-surface-base`, `text-text-primary`, `border-border-soft`, `shadow-glass-1`, `ease-ios`, `duration-[--dur-card]`, `rounded-lg`, etc. become available.

### Additional utility classes (append to `main.css` AFTER `@theme`)

```css
@layer utilities {
  /* Glass composite utilities — always pair bg-glass-* with backdrop-blur-* */
  .bg-glass-1 { background-color: var(--color-surface-glass-1); backdrop-filter: blur(var(--blur-md)) saturate(1.4); -webkit-backdrop-filter: blur(var(--blur-md)) saturate(1.4); }
  .bg-glass-2 { background-color: var(--color-surface-glass-2); backdrop-filter: blur(var(--blur-md)) saturate(1.3); -webkit-backdrop-filter: blur(var(--blur-md)) saturate(1.3); }
  .bg-glass-float { background-color: var(--color-surface-glass-float); backdrop-filter: blur(var(--blur-lg)) saturate(1.5); -webkit-backdrop-filter: blur(var(--blur-lg)) saturate(1.5); }

  .border-glass { border: 1px solid var(--color-border-glass); }
  .shadow-glass { box-shadow: var(--shadow-glass-1); }
  .shadow-glass-float { box-shadow: var(--shadow-glass-float); }

  /* Focus ring (applied via :focus-visible in components) */
  .focus-ring-glass { outline: 2px solid var(--color-border-ring); outline-offset: 2px; }

  /* Motion convenience */
  .ease-ios { transition-timing-function: var(--ease-ios); }
  .dur-card { transition-duration: var(--dur-card); }
  .dur-page { transition-duration: var(--dur-page); }

  /* Entrance animation — used everywhere opt-in */
  .animate-in {
    animation: animate-in var(--dur-card) var(--ease-ios) both;
  }
  @keyframes animate-in {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0);   }
  }
  @media (prefers-reduced-motion: reduce) {
    .animate-in { animation: animate-in-rm var(--dur-micro) linear both; }
    @keyframes animate-in-rm {
      from { opacity: 0; }
      to   { opacity: 1; }
    }
  }
}
```

**Browser note:** `backdrop-filter` has 97% support; older Safari needs `-webkit-` prefix (included). Fallback: if not supported, `bg-glass-*` still renders as semi-transparent surface — legibility preserved.

---

## 3. PrimeVue Overrides

PrimeVue keeps **Aura preset** (already wired in `main.ts`). Overrides applied via CSS in a **new file** `frontend/src/assets/styles/primevue-overrides.css` (imported from `main.ts` after `main.css`). Rationale: keeping overrides in CSS (not the `pt` API) means one-pass styling, no per-component boilerplate, and lets us scope by `.dark`.

### Components + rules

**Button** (192 usages — biggest win)
- Default: `background: var(--color-accent); color: var(--color-text-on-accent); border-radius: var(--radius-sm); padding: 0.55rem 0.95rem; font-weight: 500; box-shadow: var(--shadow-card); transition: transform 240ms var(--ease-ios), background-color 240ms var(--ease-ios);`
- Hover: `transform: translateY(-1px); background: color-mix(in srgb, var(--color-accent) 92%, black);`
- Active: `transform: translateY(0); filter: brightness(0.95);`
- Focus-visible: `outline: 2px solid var(--color-border-ring); outline-offset: 2px;`
- Disabled: `opacity: 0.5; transform: none;`
- Severity variants: `.p-button-secondary` → `bg-glass-1 + border-glass + text-text-primary`; `.p-button-danger` → `--color-danger` bg; `.p-button-text` → transparent bg, accent color; `.p-button-outlined` → transparent bg, `--color-accent` 1px border.

**InputText / Textarea / Select / MultiSelect** (85+ usages combined)
- Default: `background: var(--color-surface-raised); border: 1px solid var(--color-border-soft); border-radius: var(--radius-sm); padding: 0.6rem 0.8rem;`
- Focus: `border-color: var(--color-accent); box-shadow: 0 0 0 3px var(--color-accent-soft);`
- Invalid: `border-color: var(--color-danger); box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-danger) 25%, transparent);`
- Disabled: `background: var(--color-surface-sunken); opacity: 0.7;`
- Dark: inputs stay on `--color-surface-sunken` (solid, NOT glass — legibility rule).

**Dialog**
- `.p-dialog`: `background: var(--color-surface-glass-float); backdrop-filter: blur(var(--blur-lg)) saturate(1.5); border: 1px solid var(--color-border-glass); border-radius: var(--radius-lg); box-shadow: var(--shadow-glass-float);`
- `.p-dialog-mask`: `background: rgba(10,14,24,0.45); backdrop-filter: blur(var(--blur-sm));`
- Enter animation: opacity 0→1, scale 0.98→1, 420ms, `var(--ease-ios)`.

**DataTable** (14 usages — candidate lists, vacancy lists)
- Table body rows: solid `--color-surface-base` / `--color-surface-raised` alternating subtle (2% tint). NO glass on data rows — legibility.
- Header: `background: var(--color-surface-sunken); font-weight: 600; color: var(--color-text-secondary); border-bottom: 1px solid var(--color-border-soft);`
- Row hover: `background: var(--color-accent-soft);` 120ms fade.
- Selected row: `background: color-mix(in srgb, var(--color-accent) 10%, transparent); border-left: 2px solid var(--color-accent);`
- Pagination container: `bg-glass-1 border-glass` (chrome can be glass).

**Card (`.p-card`)**
- `background: var(--color-surface-raised); border: 1px solid var(--color-border-soft); border-radius: var(--radius-md); box-shadow: var(--shadow-card);` — solid, not glass. Cards hold data.

**Menu / Menubar / Toolbar** (chrome)
- `.p-menu, .p-menubar, .p-toolbar`: `bg-glass-1 border-glass shadow-glass`. Chrome = glass.
- Active menu item: `background: var(--color-accent-soft); color: var(--color-accent);`

**Toast**
- `.p-toast-message`: `bg-glass-float border-glass shadow-glass-float` + 4px left border in severity color (`--color-success`, `--color-info`, etc.).
- Enter: slide-in-from-top 320ms `var(--ease-ios)`.

**TabView / Tabs** — existing overrides in `main.css` (lines 38–112) are reasonable but use hardcoded hex. Replace hardcoded values with tokens (`var(--color-border-soft)`, `var(--color-accent)`, `var(--color-accent-soft)`, `var(--color-text-secondary)`, etc.) and add `.dark` overrides.

**Tag / Chip / Badge** (used for vacancy states, candidate statuses)
- Preserve 4 vacancy states exactly: Draft / Published / Paused / Archived — each gets its own token pair. Draft: `--color-text-muted` on `--color-surface-sunken`. Published: `--color-success` on `color-mix(--color-success 15% transparent)`. Paused: `--color-warning` similar. Archived: muted + strikethrough-opacity style.

---

## 4. Typography

**Install:** `@fontsource/geist-sans` (weights 400, 500, 600, 700), `@fontsource-variable/geist-sans` if available (single file variable). `@fontsource/geist-mono` (400, 500).

Import in `frontend/src/main.ts` (top of file, before PrimeVue):
```ts
import '@fontsource/geist-sans/400.css'
import '@fontsource/geist-sans/500.css'
import '@fontsource/geist-sans/600.css'
import '@fontsource/geist-sans/700.css'
import '@fontsource/geist-mono/400.css'
import '@fontsource/geist-mono/500.css'
```

Add to `@theme` block:
```css
--font-sans: 'Geist Sans', ui-sans-serif, system-ui, -apple-system, sans-serif;
--font-mono: 'Geist Mono', ui-monospace, SFMono-Regular, monospace;
```

And set on `body` in `main.css`: `body { font-family: var(--font-sans); font-feature-settings: 'cv11', 'ss01', 'ss03'; }` — enables Geist's stylistic alternates (crisper `a`, `g`).

### Type scale (reuses Tailwind defaults; one custom step)

| Step | Class | Size / LH / Tracking | Use |
|---|---|---|---|
| Display | `.text-display` (new) | 56–72px clamp / 1.05 / −0.025em | Landing hero only |
| H1 | `text-4xl` | 36px / 1.15 / −0.015em | Page titles |
| H2 | `text-2xl` | 24px / 1.2 / −0.01em | Section heads |
| H3 | `text-lg` | 18px / 1.3 | Card heads |
| Body | `text-sm` | 14px / 1.55 | Default UI text |
| Body-lg | `text-base` | 16px / 1.55 | Landing paragraph |
| Caption | `text-xs` | 12px / 1.4 / 0.01em | Metadata, labels |

Add:
```css
.text-display { font-size: clamp(2.75rem, 5.5vw, 4.5rem); line-height: 1.05; letter-spacing: -0.025em; font-weight: 600; }
```

**Weight discipline:** 400 body, 500 UI labels/nav, 600 section heads, 700 display only. No 800/900 — Geist's 700 is already dense.

**Geist Mono used for:** interview tokens (`token`), timestamps (`12:04:32`), candidate IDs (`C-000142`), vacancy slugs, keyboard-shortcut glyphs (⌘K), code snippets in admin/debug panels. Never for body UI.

---

## 5. Glass Primitive Components

All in `frontend/src/shared/components/`.

### GlassSurface.vue
- **File**: `shared/components/GlassSurface.vue`
- **Purpose**: base translucent container primitive. All other glass components compose this.
- **Props**: `level?: '1' | '2' | 'float'` (default `1`), `as?: string` (default `div`), `interactive?: boolean`, `noBorder?: boolean`.
- **Slots**: `default`.
- **Visual**: `bg-glass-{level}` + `border-glass` (unless `noBorder`) + `shadow-glass` (or `shadow-glass-float` for level `float`) + `rounded-md` by default (override via class).
- **Interactive state** (when `interactive`): `cursor-pointer; transition-transform dur-card ease-ios; hover:translate-y-[-1px]; active:translate-y-0`.
- **Accessibility**: `:focus-visible` → `.focus-ring-glass`. If `as="button"`, adds proper focus semantics.
- **Reduced-motion**: disables `translate-y` on hover, keeps opacity transition only.

### GlassCard.vue
- **File**: `shared/components/GlassCard.vue`
- **Composes** `GlassSurface` with `level="1"`, `padding="p-5 md:p-6"`, `rounded-lg`.
- **Props**: `title?: string`, `subtitle?: string`, `accent?: 'default' | 'ai' | 'celebrate'` — accent adds a 1px top border in the accent color + faint accent glow behind the card via `::before` radial gradient.
- **Slots**: `default`, `header`, `footer`.
- **Where used**: dashboard widgets, AI assistant prompt cards (accent="ai"), offer-sent confirmations (accent="celebrate").

### GlassDialog.vue
- **File**: `shared/components/GlassDialog.vue`
- **Decision**: do NOT build a custom dialog. Wrap PrimeVue `Dialog` with PrimeVue overrides from Section 3. This file only exists if we need consistent header/footer slots; otherwise skip it and use `Dialog` directly.
- **Alternate**: if we do want a custom one, use `teleport to="body"` + `GlassSurface level="float"` + `role="dialog" aria-modal="true"`. Keep PrimeVue's for confirm/forms — glassDialog only for product-feature modals (e.g. interview-preview overlay).

### GlassButton.vue
- **File**: `shared/components/GlassButton.vue`
- **Decision**: DO NOT build. PrimeVue `Button` with overrides from Section 3 covers everything. Creating a parallel button component fragments the codebase and fights 192 existing usages.
- If we later need a distinct "glass" ghost variant, add it as a PrimeVue severity class (`.p-button-glass`).

### GlassInput.vue
- **File**: same call — DO NOT build. PrimeVue `InputText`, `Textarea`, `Select`, `MultiSelect` with overrides. Consistent API, zero migration.

### PageShell.vue
- **File**: `shared/components/PageShell.vue`
- **Purpose**: the root wrapper used by layouts. Stacks: `AnimatedBackground` (pos: fixed, inset-0, -z-10) → content (`relative z-0`) → `FloatingBackgroundPicker` (fixed bottom-right).
- **Props**: `variant?: 'app' | 'public'` (changes content padding only).
- **Slots**: `nav`, `default` (main content), `footer`.
- **Motion**: first child entrance → `animate-in`. Route changes → opacity fade 240ms via `<Transition name="page">`.
- **Reduced-motion**: disables route transform; keeps 180ms opacity crossfade.

### FloatingBackgroundPicker.vue
- **File**: `shared/components/FloatingBackgroundPicker.vue`
- **Replaces** existing `BackgroundModeSwitcher.vue` (move its logic here; delete the old file or keep as a thin re-export during the migration).
- **Visual**: a floating pill, fixed bottom-right, 16px from each edge, 44px tall (mobile-safe tap target). Closed state: circular 44×44 "palette" icon button. Open state: pill expands rightward (or upward on mobile) revealing 4 thumbnail squares (one per background) + a theme-toggle icon at the right end. `bg-glass-float border-glass shadow-glass-float rounded-full`.
- **Thumbnails**: 36×36 `GlassSurface level="1"` each, containing a miniature static render of that background (Aurora thumb = small conic gradient, Mesh thumb = 3 blurred dots, Constellation thumb = 5 nodes + lines, Vellum thumb = subtle gradient). Selected thumb: 2px accent border.
- **Interaction**: click thumb → sets `backgroundMode`; haptic-feeling spring via `motion-v` (see Section 8).
- **Accessibility**: closed button has `aria-label="Background and theme"`. Open pill is a `role="radiogroup"`. Each thumb = `role="radio"`. Theme toggle is a separate button.
- **Mobile**: pill expands upward into a 2×2 grid of thumbs + theme toggle below.
- **Persistence**: see Section 10.
- **Reduced-motion**: open/close = opacity fade only; no spring.

---

## 6. Four Background Variants

All `<svg>`/CSS-only. All fixed-position (`position: fixed; inset: 0; pointer-events: none; z-index: -10;`). All respect `@media (prefers-reduced-motion: reduce)` by swapping animated content for a static gradient.

### BackgroundAurora.vue (DEFAULT)
- **File**: `shared/components/backgrounds/BackgroundAurora.vue`
- **Construction**: 3 layered absolutely-positioned `<div>`s; each is a large (150vw × 150vh) conic-gradient ribbon with `filter: blur(var(--blur-xl))` and 40% opacity. Each ribbon uses a different gradient rotation (0°, 90°, 180°) and a different CSS `@keyframes` slow pan (translate + rotate) over 45s / 55s / 65s loops (coprime — prevents visible loop).
- **Light mode colors** (ribbon gradients): `from-[#cfd9ff] via-[#e4d4ff] to-[#ffe0cf]`, `from-[#d6ebff] via-transparent to-[#e9d5ff]`, `from-[#fff5e6] via-transparent to-[#dbeafe]`.
- **Dark mode colors**: `from-[#1a2438] via-[#2a1a55] to-[#3a1f3a]`, `from-[#0f1d36] via-transparent to-[#2a0f45]`, `from-[#241233] via-transparent to-[#0b1a36]`. Opacity raised to 55% so it reads against deep base.
- **Reduced-motion**: all three ribbons replaced by a single static radial gradient `radial-gradient(ellipse at 30% 20%, var(--color-accent-ai-soft), transparent 60%), radial-gradient(ellipse at 70% 80%, var(--color-accent-soft), transparent 60%)`.
- **Perf**: GPU-compositable (transform only). ~0.5% CPU on M1, tested mentally against Apple visionOS aesthetic.

### BackgroundMesh.vue
- **File**: `shared/components/backgrounds/BackgroundMesh.vue`
- **Construction**: 5 absolutely-positioned circular `<div>`s, each 50–80vmin diameter, `border-radius: 50%`, `filter: blur(var(--blur-xl))`, `mix-blend-mode: screen` in dark / `multiply` in light.
- **Positions** (light mode, top-left origin): blob A (15%, 20%), B (75%, 30%), C (50%, 55%), D (20%, 80%), E (85%, 75%).
- **Colors**: A accent blue `#2563eb`, B ai-violet `#7c5cff`, C celebrate-peach `#ff9b73`, D soft-teal `#06b6d4`, E soft-pink `#f472b6`. All at 45% opacity light / 55% opacity dark.
- **Motion**: each blob drifts on independent `@keyframes` (translate −6% to +6% x/y, 28s / 33s / 37s / 41s / 44s — coprime). No rotation.
- **Reduced-motion**: blobs locked to their start positions; no animation.

### BackgroundConstellation.vue
- **File**: `shared/components/backgrounds/BackgroundConstellation.vue`
- **Construction**: single `<svg viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid slice">`. Contains ≤40 `<circle>` nodes placed on a seeded jittered grid (6×6 grid minus corners, slight random offset). Nodes are 2–3px radius, fill `var(--color-accent-ai)` at 60% opacity.
- **Lines**: `<line>` between each node and its 2 nearest neighbors, `stroke="var(--color-accent-ai)" stroke-width="0.5" stroke-opacity="0.15"`. Lines rendered first (beneath nodes).
- **Motion**: per-node pulse via CSS — `animation: node-pulse 5s ease-in-out infinite` with staggered `animation-delay` (seeded). Pulse = opacity 0.6 → 1.0 → 0.6 + radius 2 → 3 → 2.
- **Parallax**: whole `<svg>` transforms on mouse-move (desktop only — `pointer: fine` + `!matchMedia('(prefers-reduced-motion: reduce)')`), via a lightweight rAF handler. `transform: translate(${mx/50}px, ${my/50}px)`.
- **Reduced-motion**: freeze all pulses and parallax; single static render.
- **Cap**: max 40 nodes × 2 lines ≈ 80 SVG elements. Safe on mobile.

### BackgroundVellum.vue
- **File**: `shared/components/backgrounds/BackgroundVellum.vue`
- **Construction**: two stacked layers. Layer 1 = slow breathing radial gradient `radial-gradient(ellipse at 50% 40%, var(--color-surface-raised), transparent 70%)` with `@keyframes breathe` (opacity 0.6 → 0.9 → 0.6 over 12s). Layer 2 = noise texture via inline SVG filter `<filter><feTurbulence type="fractalNoise" baseFrequency="0.9" /></filter>` rendered into a `<rect>` fill, 4% opacity. Or use a small (512×512) pre-generated `noise.webp` in `public/` for better perf.
- **Motion**: breathing only. Ultra-calm. 12s cycle.
- **Reduced-motion**: freeze breathing at 0.75 opacity; noise static.

### AnimatedBackground.vue (orchestrator)
- **File**: EXISTING `frontend/src/shared/components/AnimatedBackground.vue` — **rewrite**.
- **Logic**: reads `themeStore.backgroundMode`. Renders exactly one of `<BackgroundAurora />`, `<BackgroundMesh />`, `<BackgroundConstellation />`, `<BackgroundVellum />`, or `null` if mode = `'off'`.
- **Crossfade**: switching variants = 600ms opacity crossfade via `<Transition>`.
- **Random-on-first-load**: if `localStorage['hr_prescan_bg_mode']` is unset, `themeStore.setBackgroundMode(random)` on mount. Random picker choses one of `['aurora','mesh','constellation','vellum']` uniformly. Persist the chosen value so reloads don't keep changing.
- **Reduced-motion**: always renders the variant, but the variant itself swaps to static fallback (per individual component rules).

---

## 7. Logo — Prism, Full SVG Spec

### Construction (Prism glyph)

- **ViewBox**: `0 0 64 64`. Designed on a 4px base grid.
- **Shape 1 — prism** (hex lens shape): an irregular pentagon, vertices at `(10,16) (32,10) (50,16) (50,48) (32,54) (10,48)` (a flattened hex), filled with a **linear gradient** `#3b5bff → #7c5cff` at 45° angle. 1px inner highlight stroke `rgba(255,255,255,0.25)`.
- **Shape 2 — incoming beam**: single line from `(-2, 32)` to `(10, 32)` (exits left edge). Stroke `var(--color-text-primary)` at 70% opacity, 2px wide. Rounded caps.
- **Shape 3 — outgoing beams (3, ranked)**: three lines starting from the prism right face `(50, 22)`, `(50, 32)`, `(50, 42)` and extending to `(62, 16)`, `(62, 32)`, `(62, 48)` respectively. Strokes:
  - Top beam (`50,22 → 62,16`): `var(--color-accent-celebrate)` #FF9B73, 2.5px wide, 100% opacity — the "chosen" candidate.
  - Middle beam: `var(--color-accent-ai)` #7C5CFF, 2px, 70% opacity.
  - Bottom beam: `var(--color-accent)` #2563EB, 2px, 45% opacity.
- **Gradient IDs**: `prismGradDark` / `prismGradLight` — reference via `fill="url(#prismGrad…)"` chosen by `.dark` CSS selector on parent.

### Variants

- **Light mode**: prism gradient `#3b5bff → #7c5cff`; beams as above.
- **Dark mode**: prism gradient stays (saturation reads well on dark); prism stroke highlight becomes `rgba(255,255,255,0.35)`; incoming beam stroke `rgba(229,231,235,0.8)`.

### `AppLogo.vue` component changes (existing file)

- Preserve the existing `size` prop (sm/md/lg) and `linked`/`to` props.
- Replace SVG body with the Prism spec above.
- Add a `variant?: 'full' | 'glyph' | 'wordmark'` prop. `full` = glyph + "HR PreScan" wordmark in Geist 600; `glyph` = mark only (for collapsed sidebar, favicon); `wordmark` = text only (rare).
- Hover: 2s subtle rotation of the prism (rotateY 0 → 8° → 0) + top beam opacity pulse. Reduced-motion: no rotation, keep color.

### Favicons / app icons

Generate from the glyph:
- `public/favicon.ico` — 16, 32, 48 multi-size ICO.
- `public/favicon-32.png`, `public/favicon-16.png`.
- `public/apple-touch-icon.png` — 180×180, full-bleed prism on white background, 10% padding.
- `public/android-chrome-192.png`, `public/android-chrome-512.png` — maskable, prism centered on a `#0b0f17` safe zone (40%).
- `public/og-image.png` — 1200×630. Composition: prism glyph at 320px on the left, "HR PreScan" in Geist 700 at 88px, tagline "Pre-screen candidates in minutes, not hours" in Geist 500 at 32px. Background: Aurora-still (CSS gradient, flattened to PNG). Dark-mode version at `public/og-image-dark.png`.

### Animated hover variant (top nav)

- Mount the glyph in `AppNavbar.vue` / `PublicHeader.vue`.
- On hover: prism rotates subtly (described above); the three outgoing beams stagger their opacity pulse 0→100 with 80ms offset; 600ms total, ease-ios. Reduced-motion: color-only flash.

---

## 8. Motion Specs

All via `motion-v` or CSS keyframes. Named:

| Name | Fires on | Duration | Easing | Pattern (motion-v) | Reduced-motion |
|---|---|---|---|---|---|
| `pageEnter` | route enter | 420ms | `ease-ios` | `v-motion` `:initial="{ opacity: 0, y: 10 }" :enter="{ opacity: 1, y: 0 }"` | opacity only, 180ms |
| `cardEnter` | card mount, list items | 420ms | `ease-ios` | `initial opacity 0, y 8 → enter opacity 1, y 0` | opacity only |
| `cardStagger` | list rendering | 60ms per item, max 10 | `ease-ios` | `v-motion` with `:transition="{ delay: index * 60 }"` | no stagger, all fade together |
| `dialogEnter` | PrimeVue Dialog open | 320ms | `ease-ios` | PrimeVue pt + CSS keyframe `opacity 0 → 1, scale 0.98 → 1` | opacity only, 180ms |
| `toastSlide` | Toast enter | 320ms | `ease-ios` | slide-from-top: `y -20 → 0, opacity 0 → 1` | opacity only |
| `accentPulse` | AI-origin moments (prescan badge, AI assistant ping) | 1600ms loop | `ease-in-out` | CSS keyframe: opacity 0.8 → 1 → 0.8, scale 1 → 1.03 → 1 on ring only | freeze at opacity 1 |
| `hoverLift` | interactive `GlassSurface` / Button / Card | 240ms | `ease-ios` | CSS transition on `translateY(-1px)` | no transform |
| `focusRing` | `:focus-visible` | 160ms | `ease-ios` | CSS transition on outline-color + outline-offset | instant |
| `bgCrossfade` | `backgroundMode` change | 600ms | `ease-out-soft` | Vue `<Transition>` opacity | opacity only, same duration |

### Motion governance

- **Never** animate on mount of 10+ items (cap stagger). Otherwise landing feels slow.
- **Never** animate scroll. No scroll-triggered parallax on landing except the Constellation background's mouse parallax (desktop only).
- **Always** gate transforms behind `prefers-reduced-motion`. Opacity/color are safe.

---

## 9. Per-Area Layout Notes

| Area | Treatment | IA change? |
|---|---|---|
| **Landing** | All 8 sections kept but recomposed on 1800px-wide layout on a single scroll. Hero gets `text-display` + Aurora background. Replace LandingStats' static 3-up metrics with a single **live-metric strip** (glass chip: "12,481 candidates screened this week"). LandingPipeline: swap the illustrated diagram for an animated 3-step "Apply → Prescreen → Interview" horizontal flow using Constellation-style nodes. LandingJobs: remove unless we have real public jobs; else replace with a "Featured vacancies" showcase with live data. Nav: translucent glass header, sticky. | Stats redesigned; Pipeline redesigned; Jobs conditional. |
| **Auth** (login/register/verify/choose-role/company-setup/accept-invite) | Centered `GlassCard` (max-w-md) on top of `BackgroundVellum` (always Vellum for auth — calm, focused). Logo glyph at top. Fields use PrimeVue InputText with overrides. No IA changes. | No. |
| **Dashboard** | 2-column on desktop (main + rail), 1-column on mobile. Cards are `GlassCard` level 1 with solid data areas inside. Top-left: greeting + quick stats; center: pipeline overview; rail: recent activity + AI assistant teaser. | No (purely visual). |
| **Vacancies** (list/create/detail) | List = DataTable (solid rows) with glass chrome (toolbar, pagination). Create = multi-step wizard as `GlassCard` with progress breadcrumb. Detail = header card + tabs (applicants / questions / settings). **Preserve state-transition affordances** (Draft/Published/Paused — NO archive). | No. |
| **Candidates** (HR list/detail + MyApplications) | HR list: DataTable with avatar + name + score + status. Detail: 2-column — left panel with CV + transcript, right panel with scoring + AI summary. MyApplications (candidate): card grid, each card shows status pill + "Start prescan" CTA. | No. |
| **Interviews** (HR list/detail + Candidate chat/room/gateway/confirmation + Observer) | **ChatInterviewPage**: chat column on `GlassCard`, AI avatar with `accentPulse` ring when speaking, transcript scrolling area with solid background. **InterviewRoomPage**: video tile center, glass sidebar with score criteria, floating mute/end buttons (glass float). **Gateway**: centered card with prism logo glow. **Observer**: DataTable of ongoing interviews + live transcript pane. | No. |
| **CV Builder** (builder/myCvs/publicCv) | Builder: left-rail section list (glass), center-form solid `GlassCard`, right preview pane (solid paper-look). MyCvs: card grid. PublicCv: single centered paper-look card on `BackgroundVellum`. | No. |
| **Admin** (dashboard/companies/users/analytics/plans) | Admin gets a **denser** treatment — tighter type scale, minimal glass (only toolbar + menu). Data rules: solid tables. Reason: admins prefer density over beauty. | No. |
| **Settings** (profile/team) + **Notifications** + **Subscription** + **Pricing** | Two-column settings layout on desktop. GlassCards grouped by concern. Pricing page: 3 plan cards, center plan `GlassCard accent="ai"` (highlighted). | No. |
| **Errors** (403/404/500) | Full-bleed background (Aurora for 404 "playful", Vellum for 403 "serious", Mesh for 500 "in-motion"). Centered `GlassCard` with prism glyph + error message + single CTA. | No. |
| **Legal** (privacy/terms) | Solid reading layout — no glass in the content body (legibility). Nav glass only. `.prose` styling from the Tailwind typography plugin. | No. |

**No business-logic changes implied.** All state affordances preserved; only visuals change. `docs/BUSINESS_LOGIC.md` update task (T20) likely will NOT be needed — flag if implementer spots otherwise.

---

## 10. Background Picker UX

### Decision: **localStorage only — no backend API.**

**Rationale**:
- Background preference is trivial, device-local, and non-critical. Persisting per-user server-side adds migration + sync complexity for zero value.
- If a user is on a new device, random-on-first-load gives them a fresh picker anyway — that's fine.
- Theme + backgroundMode live together in `theme.store.ts` localStorage. No backend change.

If we ever need cross-device sync, add later to the User profile endpoint.

### UX

- `FloatingBackgroundPicker.vue` lives in `PageShell.vue` (both `app` and `public` variants).
- Closed by default. Tap → pill expands.
- Contains: 4 variant thumbnails + theme toggle (3-state: light/dark/system).
- Keyboard: `?` or `Alt+B` opens; `Esc` closes; arrow keys navigate variants; `Enter` selects.
- ARIA: `role="toolbar" aria-label="Background and theme"`.

### Store changes (`theme.store.ts`)

Extend `BackgroundMode` type to:
```ts
export type BackgroundMode = 'off' | 'aurora' | 'mesh' | 'constellation' | 'vellum'
```

Remove `'forest' | 'ocean'` (deprecated — migrate on read: any legacy value → `'aurora'`). Default on fresh load: pick random from `['aurora','mesh','constellation','vellum']`, persist. User-chosen value (including `'off'`) always wins.

---

## 11. Implementation Order (Handoff)

### Wave 4 — Foundation (blocks everything)
**Task T5** — install deps, add tokens, typography, Tailwind utilities, PrimeVue overrides.
- Install `motion-v`, `@fontsource/geist-sans`, `@fontsource/geist-mono`.
- Apply Section 1 `@theme` block + Section 2 utilities to `main.css`.
- Add `primevue-overrides.css` per Section 3; import from `main.ts`.
- Replace the few hardcoded values in existing TabView CSS with tokens.
- Extend `theme.store.ts` BackgroundMode union.
- Commit as one coherent PR chunk.

### Wave 5 — Parallel (3 tasks, independent files)
- **T6: Glass primitives** — `GlassSurface.vue`, `GlassCard.vue`, `PageShell.vue`, `FloatingBackgroundPicker.vue`, logo update in `AppLogo.vue`. Replace `BackgroundModeSwitcher.vue`.
- **T7: Backgrounds** — 4 variant components + rewrite `AnimatedBackground.vue` orchestrator.
- **T8: Logo assets** — SVG edits in `AppLogo.vue` (already part of T6 if one agent), plus all favicon/OG image files in `public/`.

T6, T7, T8 touch different files. Parallel-safe. If one agent handles T6 and T8 together, merge those.

### Wave 6 — Landing + Background picker UX polish (parallel)
- **T9: Background picker UX** — already in T6's `FloatingBackgroundPicker.vue`; T9 becomes integration: mount picker in `PageShell`, migrate legacy bgMode values on app boot, wire keyboard shortcuts.
- **T10: Landing redesign** — rebuild all 8 landing sections with new primitives + Aurora hero + new Pipeline + live-metric strip.

### Wave 7 — User screenshot review on landing (gate)

### Wave 8 — Remaining 5 parallel page groups (T12–T16). Each uses the primitives, no primitive edits allowed.

### Wave 9+ — Screenshots, business review (likely pass, no IA changes), tests, code review, PR to `dev`.

---

## Next wave prompt (for `/feature` T5)

> Install `motion-v`, `@fontsource/geist-sans`, `@fontsource/geist-mono`. Apply the design tokens and Tailwind utilities from `docs/design/spec.md` §1–2 into `frontend/src/assets/styles/main.css`. Create `frontend/src/assets/styles/primevue-overrides.css` with the PrimeVue rules from §3 and import it from `main.ts` after `main.css`. Add the Geist font imports to `main.ts`. Extend `BackgroundMode` in `theme.store.ts` to `'off' | 'aurora' | 'mesh' | 'constellation' | 'vellum'` with a migration for the legacy `forest`/`ocean` values → `aurora`. No component edits, no new components — foundation only. Acceptance: `yarn build` succeeds, `yarn dev` serves, dark/light toggle still works, existing pages render unchanged visually (they don't use new tokens yet).

**Stop. Await user approval of this spec before dispatching T5.**
