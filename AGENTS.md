# HR PreScan — Agent Team Architecture

## Overview

Development is done by a team of specialized Claude Code agents, each with a focused role. They coordinate via GitHub Issues and Pull Requests, mimicking a real engineering team.

---

## Agent Roles

### PM Agent (Project Manager / Orchestrator)

**Responsibilities:**
- Read `ROADMAP.md` and identify current phase tasks
- Create GitHub Issues for each task (with labels: `backend`, `frontend`, `devops`)
- Assign issues to appropriate engineer agents
- Review PRs from engineer agents (check code quality, adherence to CODE_STYLE.md)
- Merge approved PRs
- Update `ROADMAP.md` checkboxes after tasks are completed
- Resolve conflicts between agents (e.g., API contract disagreements)

**Has access to:** All project docs (BUSINESS_LOGIC.md, TECH_ARCHITECTURE.md, CODE_STYLE.md, DEVOPS.md, ROADMAP.md)

**Does NOT:** Write application code directly

### Backend Engineer Agent

**Responsibilities:**
- Django models, services, selectors, APIs, serializers
- Celery tasks
- Database migrations
- Integration wrappers (LiveKit, Deepgram, OpenAI, ElevenLabs, MinIO)
- Backend-specific configuration

**Reads:** BUSINESS_LOGIC.md, TECH_ARCHITECTURE.md, CODE_STYLE.md (Django sections)
**Works in:** `backend/` directory
**Branch prefix:** `be/`

### Frontend Engineer Agent

**Responsibilities:**
- Vue.js pages, components, composables
- Pinia stores
- API service layer (Axios)
- TypeScript types
- PrimeVue + Tailwind styling
- Vue Router routes and guards

**Reads:** BUSINESS_LOGIC.md, TECH_ARCHITECTURE.md, CODE_STYLE.md (Vue sections)
**Works in:** `frontend/` directory
**Branch prefix:** `fe/`

### DevOps Engineer Agent

**Responsibilities:**
- Dockerfiles, docker-compose files
- Nginx configuration
- CI/CD pipelines (GitHub Actions)
- Monitoring setup (Grafana, Prometheus, Jaeger, Loki)
- Management UI configuration (Portainer, pgAdmin, RedisInsight)
- Backup scripts
- SSL/TLS setup

**Reads:** DEVOPS.md, TECH_ARCHITECTURE.md
**Works in:** Root directory, `scripts/`, `.github/`
**Branch prefix:** `devops/`

---

## Workflow

### Starting a Phase

```
1. Human says: "Start Phase N"
2. PM Agent:
   a. Reads ROADMAP.md Phase N tasks
   b. Groups tasks by role (backend, frontend, devops)
   c. Creates GitHub Issues for each task
   d. Labels issues: backend/frontend/devops + phase-N
   e. Reports task assignments to human

3. Engineer agents work in parallel:
   - Backend Engineer: picks be/ issues → branch → code → PR
   - Frontend Engineer: picks fe/ issues → branch → code → PR
   - DevOps Engineer: picks devops/ issues → branch → code → PR

4. PM Agent:
   a. Reviews each PR (code quality, style compliance)
   b. Requests changes if needed
   c. Merges approved PRs
   d. Checks off ROADMAP.md tasks
   e. Reports phase completion
```

### Task Dependencies

Some tasks must be sequential (e.g., backend API must exist before frontend can consume it). The PM Agent handles this by:

1. Creating backend tasks first
2. Waiting for backend PR to merge
3. Then creating dependent frontend tasks

**Dependency notation in issues:**
```
Blocked by: #12 (backend vacancy API)
```

### Git Branching Strategy

```
main (protected)
├── be/phase2-user-model          # Backend task branch
├── be/phase2-jwt-auth            # Backend task branch
├── fe/phase2-login-page          # Frontend task branch
├── fe/phase2-auth-store          # Frontend task branch
├── devops/phase1-docker-compose  # DevOps task branch
└── ...
```

**Branch naming:** `{role}/{phaseN}-{short-description}`

**Rules:**
- All branches created from latest `main`
- PRs require PM review before merge
- Squash merge to keep history clean
- Delete branches after merge

---

## Running Agents

### Agent Launch Script

Each agent is launched as a separate Claude Code CLI process with a role-specific system prompt.

```bash
# scripts/run_agent.sh

#!/bin/bash
AGENT_ROLE=$1
PROJECT_DIR="/Users/bakhromachilov/startups/hr_prescan"

case $AGENT_ROLE in
  pm)
    claude --system-prompt "$(cat agents/pm.md)" --cwd "$PROJECT_DIR"
    ;;
  backend)
    claude --system-prompt "$(cat agents/backend.md)" --cwd "$PROJECT_DIR"
    ;;
  frontend)
    claude --system-prompt "$(cat agents/frontend.md)" --cwd "$PROJECT_DIR"
    ;;
  devops)
    claude --system-prompt "$(cat agents/devops.md)" --cwd "$PROJECT_DIR"
    ;;
  *)
    echo "Usage: ./run_agent.sh {pm|backend|frontend|devops}"
    exit 1
    ;;
esac
```

### Running the Team

```bash
# Terminal 1: PM Agent (orchestrator)
./scripts/run_agent.sh pm

# Terminal 2: Backend Engineer
./scripts/run_agent.sh backend

# Terminal 3: Frontend Engineer
./scripts/run_agent.sh frontend

# Terminal 4: DevOps Engineer (when needed)
./scripts/run_agent.sh devops
```

### Typical Session Flow

```
Terminal 1 (PM):    "Start Phase 2. Create issues and assign tasks."
                     → Creates 13 GitHub Issues
                     → Reports: "BE has 9 tasks, FE has 4 tasks"

Terminal 2 (BE):    "Pick your assigned issues and start working."
                     → Creates branch be/phase2-user-model
                     → Writes models, services, selectors, APIs
                     → Opens PR #1

Terminal 3 (FE):    "Pick your assigned issues and start working."
                     → Creates branch fe/phase2-login-page
                     → Writes pages, components, stores
                     → Opens PR #2

Terminal 1 (PM):    "Review PR #1 and PR #2"
                     → Reviews code quality
                     → Approves and merges
                     → Updates ROADMAP.md
```

---

## API Contract Coordination

When backend and frontend work in parallel, they need to agree on API contracts. The PM Agent handles this by:

1. Before engineers start, PM creates an **API contract** (based on TECH_ARCHITECTURE.md Section 7)
2. Backend builds the API to match the contract
3. Frontend builds against the same contract
4. If either side needs changes, they update the contract via a PR

**Contract location:** `docs/api-contracts/` (simple markdown or OpenAPI/Swagger files)

---

## Agent Prompt Structure

Each agent's prompt file (`agents/*.md`) includes:

1. **Role definition** — who you are, what you do
2. **Project context** — which docs to read
3. **Working directory** — where to write code
4. **Code style** — relevant sections from CODE_STYLE.md
5. **Git workflow** — branching, commit messages, PR format
6. **Boundaries** — what you should NOT do (e.g., backend agent should not touch frontend code)
7. **Communication** — how to report status, ask for help

---

## When to Use Which Agent

| Task Type | Agent |
|-----------|-------|
| Django models, migrations | Backend |
| DRF APIs, serializers | Backend |
| Celery tasks | Backend |
| External API integrations | Backend |
| Vue components, pages | Frontend |
| Pinia stores | Frontend |
| TypeScript types | Frontend |
| Tailwind/PrimeVue styling | Frontend |
| Dockerfiles, docker-compose | DevOps |
| CI/CD pipelines | DevOps |
| Nginx config | DevOps |
| Monitoring setup | DevOps |
| Task planning, issue creation | PM |
| Code review, PR merge | PM |
| Roadmap updates | PM |
| Architecture decisions | PM + relevant engineer |
