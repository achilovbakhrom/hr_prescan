# HR PreScan — Code Style & Architecture Guide

## 0. Core Principles

All code must follow these principles:

### SOLID
- **S — Single Responsibility:** Each class, function, and module does one thing. A service handles one domain, a component renders one concern.
- **O — Open/Closed:** Extend behavior through new classes/composables, not by modifying existing ones. Use strategy patterns for evaluation criteria, notification channels, etc.
- **L — Liskov Substitution:** Subclasses/implementations must be interchangeable. If `NotificationService` has subclasses (email, in-app), they must honor the same contract.
- **I — Interface Segregation:** Don't force dependencies on unused interfaces. Keep serializers, permissions, and service interfaces focused and small.
- **D — Dependency Inversion:** High-level modules (services) should not depend on low-level modules (API clients) directly. Use the `integrations/` layer to abstract external services.

### KISS (Keep It Simple, Stupid)
- Choose the simplest solution that works. No premature abstractions.
- If a function is hard to explain, it's too complex — break it down.
- Avoid clever code. Readable > short.

### DRY (Don't Repeat Yourself)
- Extract shared logic into services, composables, or utils — but only after the second repetition (Rule of Three).
- Don't DRY across unrelated domains — similar code in different contexts is fine.
- Prefer duplication over the wrong abstraction.

---

## 1. Architecture Overview

### Backend: Service Layer Pattern (HackSoft Style)

Business logic lives in **services** (writes) and **selectors** (reads). Models stay thin. Views stay thin.

```
Request → API View (validation) → Service (logic) → Model (data) → Response
                                → Selector (query) ──────────────►
```

| Layer | Responsibility | Rules |
|-------|---------------|-------|
| **Models** | Fields, constraints, `__str__`, properties | No business logic. No external calls. |
| **Services** | All write operations, orchestration | Can call other services, selectors, integrations, dispatch tasks |
| **Selectors** | All read/query operations | Return QuerySets. Handle tenant scoping. No side effects. |
| **APIs** | HTTP concerns only: validation, permissions, status codes | Must call services/selectors. No raw ORM queries. |
| **Tasks** | Celery async wrappers | Thin — fetch objects, call services. No business logic. |
| **Integrations** | External API wrappers | One file per service. Return domain-friendly data. |

### Frontend: Feature-Based Modules (Vue.js 3)

Code is organized by domain feature, not by technical role.

```
User action → Component → Store (Pinia) → API Service → Backend
                        → Composable (reusable logic)
```

| Layer | Responsibility | Rules |
|-------|---------------|-------|
| **Pages** | Route-level components | Compose feature components. Minimal logic. |
| **Components** | UI building blocks | Props in, events out. No direct API calls. |
| **Stores** | State management (Pinia) | Call API services. Expose state + actions. |
| **Services** | API call functions | Typed request/response. Use shared Axios client. |
| **Composables** | Reusable stateful logic (`use*`) | Can use stores, refs, lifecycle hooks. |
| **Types** | TypeScript interfaces/types | Co-located with features or in `shared/types/`. |

---

## 2. Backend Project Structure (Django)

```
backend/
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── local.py
│   │   ├── production.py
│   │   └── test.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── celery.py
│
├── apps/
│   ├── common/                      # Shared: base models, permissions, utils
│   │   ├── models.py                # BaseModel (id, created_at, updated_at)
│   │   ├── permissions.py
│   │   ├── pagination.py
│   │   ├── exceptions.py
│   │   └── utils.py
│   │
│   ├── accounts/                    # Users, companies, auth
│   │   ├── models.py
│   │   ├── services.py
│   │   ├── selectors.py
│   │   ├── apis.py
│   │   ├── serializers.py
│   │   ├── permissions.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── tasks.py
│   │   ├── managers.py
│   │   └── tests/
│   │       ├── test_services.py
│   │       ├── test_selectors.py
│   │       ├── test_apis.py
│   │       └── factories.py
│   │
│   ├── vacancies/                   # Vacancies, criteria, questions
│   ├── applications/                # Candidate applications, CV
│   ├── interviews/                  # Scheduling, execution, scoring
│   ├── notifications/               # Email + in-app + SSE
│   └── subscriptions/               # Plans, billing, limits
│
├── integrations/                    # External service wrappers
│   ├── livekit.py
│   ├── storage.py
│   ├── email.py
│   ├── openai_client.py
│   ├── deepgram_client.py
│   └── elevenlabs_client.py
│
├── manage.py
├── pyproject.toml
├── Dockerfile
├── conftest.py
└── .pre-commit-config.yaml
```

### App Structure Rules

Every Django app follows the same file layout:

| File | Purpose |
|------|---------|
| `models.py` | Django models (thin) |
| `services.py` | Write operations + business logic |
| `selectors.py` | Read operations (QuerySets) |
| `apis.py` | DRF API views |
| `serializers.py` | Input/output serializers |
| `permissions.py` | DRF permission classes (if app-specific) |
| `urls.py` | URL patterns |
| `admin.py` | Django admin config |
| `tasks.py` | Celery tasks |
| `managers.py` | Custom QuerySet managers (if needed) |
| `tests/` | Test directory with `factories.py` |

---

## 3. Frontend Project Structure (Vue.js)

```
frontend/
├── src/
│   ├── app/
│   │   ├── App.vue
│   │   ├── router.ts
│   │   └── main.ts
│   │
│   ├── features/
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   ├── composables/
│   │   │   ├── pages/
│   │   │   ├── stores/
│   │   │   ├── services/
│   │   │   ├── types/
│   │   │   └── routes.ts
│   │   │
│   │   ├── dashboard/
│   │   ├── vacancies/
│   │   ├── candidates/
│   │   ├── interviews/
│   │   ├── notifications/
│   │   └── video/
│   │
│   ├── shared/
│   │   ├── api/
│   │   │   └── client.ts            # Axios instance + interceptors
│   │   ├── components/              # Layout, common UI wrappers
│   │   ├── composables/             # usePermissions, useApiError, etc.
│   │   ├── types/
│   │   ├── utils/
│   │   └── constants/
│   │
│   └── assets/
│       ├── styles/
│       └── images/
│
├── index.html
├── vite.config.ts
├── tsconfig.json
├── eslint.config.js
├── .prettierrc
├── package.json
└── Dockerfile
```

### Feature Module Rules

Every feature module follows the same layout:

| Folder | Purpose |
|--------|---------|
| `components/` | Feature-specific Vue components |
| `composables/` | Feature-specific `use*` functions |
| `pages/` | Route-level page components |
| `stores/` | Pinia stores for this feature |
| `services/` | API call functions (typed) |
| `types/` | TypeScript interfaces for this feature |
| `routes.ts` | Feature routes (lazy-loaded) |

---

## 4. Code Patterns & Examples

### 4.1 Django: Service

```python
# apps/interviews/services.py

from apps.interviews.models import Interview, InterviewScore
from apps.notifications.services import send_notification
from integrations.livekit import livekit_client


def schedule_interview(
    *, application: Application, scheduled_at: datetime
) -> Interview:
    """Create interview, generate LiveKit room, send notifications."""
    _validate_scheduling_quota(application.vacancy.company)

    interview = Interview.objects.create(
        application=application,
        scheduled_at=scheduled_at,
        status=InterviewStatus.SCHEDULED,
    )

    room_name = livekit_client.create_room(interview_id=interview.id)
    interview.livekit_room_name = room_name
    interview.save(update_fields=["livekit_room_name"])

    send_interview_scheduled_notification.delay(interview.id)

    return interview
```

### 4.2 Django: Selector

```python
# apps/interviews/selectors.py

from django.db.models import QuerySet
from apps.interviews.models import Interview


def get_company_interviews(
    *, company: Company, status: str | None = None
) -> QuerySet[Interview]:
    qs = Interview.objects.filter(
        application__vacancy__company=company,
    ).select_related("application__vacancy", "application")

    if status:
        qs = qs.filter(status=status)

    return qs
```

### 4.3 Django: API View

```python
# apps/interviews/apis.py

from rest_framework.views import APIView
from rest_framework import serializers, status
from rest_framework.response import Response

from apps.interviews.services import schedule_interview
from apps.common.permissions import IsHRManager


class InterviewScheduleApi(APIView):
    permission_classes = [IsHRManager]

    class InputSerializer(serializers.Serializer):
        scheduled_at = serializers.DateTimeField()

    def post(self, request, application_id):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        application = get_object_or_404(
            Application,
            id=application_id,
            vacancy__company=request.user.company,
        )

        interview = schedule_interview(
            application=application,
            scheduled_at=serializer.validated_data["scheduled_at"],
        )

        return Response(
            InterviewDetailSerializer(interview).data,
            status=status.HTTP_201_CREATED,
        )
```

### 4.4 Django: Celery Task

```python
# apps/interviews/tasks.py

from celery import shared_task


@shared_task
def process_interview_results(interview_id: int, scores: dict, transcript: list):
    from apps.interviews.models import Interview
    from apps.interviews.services import complete_interview

    interview = Interview.objects.get(id=interview_id)
    complete_interview(interview=interview, scores=scores, transcript=transcript)
```

### 4.5 Vue: Page Component

```vue
<!-- features/candidates/pages/CandidateListPage.vue -->

<script setup lang="ts">
import { onMounted } from 'vue'
import { useCandidateStore } from '../stores/candidate.store'
import CandidateTable from '../components/CandidateTable.vue'
import CandidateFilters from '../components/CandidateFilters.vue'

const props = defineProps<{ vacancyId: string }>()
const candidateStore = useCandidateStore()

onMounted(() => {
  candidateStore.fetchCandidates(props.vacancyId)
})
</script>

<template>
  <div>
    <h1>Candidates</h1>
    <CandidateFilters @filter="candidateStore.applyFilters" />
    <CandidateTable
      :candidates="candidateStore.candidates"
      :loading="candidateStore.loading"
    />
  </div>
</template>
```

### 4.6 Vue: Pinia Store

```typescript
// features/candidates/stores/candidate.store.ts

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { candidateService } from '../services/candidate.service'
import type { Candidate, CandidateFilters } from '../types/candidate.types'

export const useCandidateStore = defineStore('candidate', () => {
  const candidates = ref<Candidate[]>([])
  const loading = ref(false)

  async function fetchCandidates(vacancyId: string) {
    loading.value = true
    try {
      candidates.value = await candidateService.getByVacancy(vacancyId)
    } finally {
      loading.value = false
    }
  }

  async function applyFilters(filters: CandidateFilters) {
    loading.value = true
    try {
      candidates.value = await candidateService.getByVacancy(
        filters.vacancyId,
        filters,
      )
    } finally {
      loading.value = false
    }
  }

  return { candidates, loading, fetchCandidates, applyFilters }
})
```

### 4.7 Vue: API Service

```typescript
// features/candidates/services/candidate.service.ts

import { apiClient } from '@/shared/api/client'
import type { Candidate, CandidateFilters } from '../types/candidate.types'

export const candidateService = {
  async getByVacancy(
    vacancyId: string,
    filters?: CandidateFilters,
  ): Promise<Candidate[]> {
    const { data } = await apiClient.get(
      `/hr/vacancies/${vacancyId}/candidates/`,
      { params: filters },
    )
    return data.results
  },

  async getDetail(candidateId: string): Promise<Candidate> {
    const { data } = await apiClient.get(`/hr/candidates/${candidateId}/`)
    return data
  },

  async updateStatus(candidateId: string, status: string): Promise<void> {
    await apiClient.patch(`/hr/candidates/${candidateId}/status/`, { status })
  },
}
```

### 4.8 Vue: Composable

```typescript
// shared/composables/useSSE.ts

import { ref, onUnmounted } from 'vue'

export function useSSE(url: string) {
  const events = ref<any[]>([])
  const connected = ref(false)
  let source: EventSource | null = null

  function connect() {
    source = new EventSource(url)
    source.onopen = () => (connected.value = true)
    source.onmessage = (event) => {
      events.value.push(JSON.parse(event.data))
    }
    source.onerror = () => (connected.value = false)
  }

  function disconnect() {
    source?.close()
    connected.value = false
  }

  onUnmounted(disconnect)

  return { events, connected, connect, disconnect }
}
```

### 4.9 Vue: Axios Client

```typescript
// shared/api/client.ts

import axios from 'axios'
import { useAuthStore } from '@/features/auth/stores/auth.store'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL + '/api',
  headers: { 'Content-Type': 'application/json' },
})

apiClient.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const auth = useAuthStore()
      await auth.refreshToken()
    }
    return Promise.reject(error)
  },
)
```

---

## 5. Coding Rules

### 5.1 Django (Python)

- Use **keyword-only arguments** in services and selectors: `def create_vacancy(*, company, title, ...)`
- Use `update_fields` in `.save()` calls — never save full objects when updating specific fields
- Use `select_related` / `prefetch_related` in selectors — avoid N+1 queries
- Use **plain `Serializer`** for input validation, `ModelSerializer` only for read output
- Use **`APIView`** over `ViewSet` — explicit routing, no magic
- All tenant-scoped queries must filter by `company_id` in selectors
- Imports: use absolute imports (`from apps.interviews.services import ...`)
- Type hints on all service/selector function signatures
- **No hardcoded strings** — use `TextChoices` / `IntegerChoices` enums for statuses, roles, and any repeated string values:
  ```python
  # apps/interviews/models.py
  class InterviewStatus(models.TextChoices):
      SCHEDULED = "scheduled"
      IN_PROGRESS = "in_progress"
      COMPLETED = "completed"
      NO_SHOW = "no_show"
      CANCELLED = "cancelled"

  class Interview(BaseModel):
      status = models.CharField(max_length=20, choices=InterviewStatus.choices)
  ```

### 5.2 Vue.js (TypeScript)

- Use **Composition API** with `<script setup>` — no Options API
- Use **`ref`** over `reactive` for consistency
- Use **`defineProps<{...}>()`** type-only syntax — no runtime prop validation
- Components: **PascalCase** filenames (`CandidateTable.vue`)
- Composables: **camelCase** with `use` prefix (`useAuth.ts`)
- No direct API calls from components — always go through stores or composables
- Lazy-load routes: `() => import('./pages/Page.vue')`
- **No `any` type** — use `unknown` if the type is truly uncertain, then narrow it with type guards. `any` disables all type safety.
- **No inline types** — define all interfaces and types in dedicated `types/` files within each feature module. Do not define types inline in components, stores, or services.
- **Use enums/constants for repeated values** — statuses, roles, event names, route names:

  ```typescript
  // shared/constants/roles.ts
  export const UserRole = {
    ADMIN: 'admin',
    HR: 'hr',
    CANDIDATE: 'candidate',
  } as const
  export type UserRole = (typeof UserRole)[keyof typeof UserRole]

  // features/candidates/types/candidate.types.ts
  export interface Candidate {
    id: string
    name: string
    email: string
    status: CandidateStatus
    scores: InterviewScore[]
  }

  export type CandidateStatus =
    | 'applied'
    | 'interview_scheduled'
    | 'interview_completed'
    | 'reviewing'
    | 'shortlisted'
    | 'rejected'
  ```

### 5.3 File Size & Splitting

- **Keep files small and focused.** If a file grows beyond ~200-300 lines, split it.
- **Django:** If `services.py` gets large, convert to a `services/` package with files per domain area (e.g., `services/scheduling.py`, `services/scoring.py`). Same for `selectors.py`, `apis.py`, `serializers.py`.
- **Vue:** If a component exceeds ~150 lines, extract sub-components. If a store gets large, split into multiple stores.
- **Splitting pattern for Django:**
  ```
  # Before (single file)
  apps/interviews/services.py        # 400 lines, too big

  # After (package)
  apps/interviews/services/
  ├── __init__.py                    # re-exports public functions
  ├── scheduling.py                  # schedule_interview, cancel_interview
  ├── scoring.py                     # complete_interview, calculate_scores
  └── livekit.py                     # create_room, generate_token
  ```
- **Rule of thumb:** One file = one clear responsibility. If you can't describe what a file does in one sentence, it's doing too much.

### 5.4 General

- No commented-out code in commits
- No `console.log` in production code (use proper logging)
- No hardcoded strings for statuses/roles — use constants/enums
- Error messages should be user-friendly, not technical

---

## 6. Tooling Configuration

### 6.1 Backend: `pyproject.toml`

```toml
[tool.ruff]
target-version = "py312"
line-length = 120

[tool.ruff.lint]
select = [
    "E", "W",       # pycodestyle
    "F",             # pyflakes
    "I",             # isort
    "UP",            # pyupgrade
    "B",             # flake8-bugbear
    "SIM",           # flake8-simplify
    "DJ",            # flake8-django
]

[tool.ruff.lint.isort]
known-first-party = ["apps", "config", "integrations"]

[tool.mypy]
python_version = "3.12"
plugins = ["mypy_django_plugin.main", "mypy_drf_plugin.main"]
strict = false
warn_return_any = true
warn_unused_configs = true

[tool.django-stubs]
django_settings_module = "config.settings.local"

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
python_files = ["test_*.py"]
addopts = "--reuse-db --no-migrations -x -v"
```

### 6.2 Frontend: `eslint.config.js`

```javascript
import pluginVue from 'eslint-plugin-vue'
import tseslint from 'typescript-eslint'
import prettierConfig from 'eslint-config-prettier'

export default [
  ...tseslint.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  prettierConfig,
  {
    rules: {
      'vue/multi-word-component-names': 'off',
      'vue/no-unused-vars': 'error',
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    },
  },
]
```

### 6.3 Frontend: `.prettierrc`

```json
{
  "semi": false,
  "singleQuote": true,
  "trailingComma": "all",
  "printWidth": 100,
  "tabWidth": 2
}
```

### 6.4 Pre-commit: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
        additional_dependencies:
          - django-stubs
          - djangorestframework-stubs

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v9.15.0
    hooks:
      - id: eslint
        files: \.(vue|ts|js)$

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v4.0.0
    hooks:
      - id: prettier
        files: \.(vue|ts|js|json|css|scss)$
```

---

## 7. Testing Strategy

### MVP Phase: No Unit Tests

For the MVP, we skip unit tests to move fast. Code quality is enforced by:
- **Linters** (Ruff, ESLint) — catch bugs and bad patterns at commit time
- **Formatters** (Ruff formatter, Prettier) — consistent code style automatically
- **Type checking** (mypy, vue-tsc) — catch type errors before runtime
- **Pre-commit hooks** — all checks run before every commit
- **CI pipeline** — lint + format + type checks block merges if they fail

### Post-MVP: Add Tests Gradually

| What | How | When to Add |
|------|-----|-------------|
| Services | `pytest` + `factory_boy` | After MVP, highest priority |
| Composables | `vitest` | After MVP |
| API endpoints | `pytest` + DRF test client | When adding complex flows |
| E2E | Playwright | When user base grows |

---

## 8. Naming Conventions

| What | Backend (Python) | Frontend (TypeScript/Vue) |
|------|-----------------|--------------------------|
| Files | `snake_case.py` | `PascalCase.vue`, `camelCase.ts` |
| Classes | `PascalCase` | `PascalCase` |
| Functions | `snake_case` | `camelCase` |
| Variables | `snake_case` | `camelCase` |
| Constants | `UPPER_SNAKE_CASE` | `UPPER_SNAKE_CASE` |
| URLs | `/api/kebab-case/` | `/kebab-case` |
| DB tables | `app_name_model_name` (Django default) | — |
| Components | — | `PascalCase.vue` |
| Composables | — | `useCamelCase.ts` |
| Stores | — | `camelCase.store.ts` |
| Services | — | `camelCase.service.ts` |
| Types | — | `camelCase.types.ts` |
