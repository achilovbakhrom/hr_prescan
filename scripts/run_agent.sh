#!/bin/bash

# HR PreScan — Agent Team Launcher
# Usage: ./scripts/run_agent.sh {pm|backend|frontend|devops}

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
AGENTS_DIR="$PROJECT_DIR/agents"

AGENT_ROLE="${1:-}"

if [ -z "$AGENT_ROLE" ]; then
  echo "Usage: ./scripts/run_agent.sh {pm|backend|frontend|devops}"
  echo ""
  echo "Agents:"
  echo "  pm        — Project Manager (creates issues, reviews PRs, manages roadmap)"
  echo "  backend   — Backend Engineer (Django, DRF, Celery)"
  echo "  frontend  — Frontend Engineer (Vue.js, TypeScript, Pinia)"
  echo "  devops    — DevOps Engineer (Docker, CI/CD, monitoring)"
  exit 1
fi

case "$AGENT_ROLE" in
  pm)
    PROMPT_FILE="$AGENTS_DIR/pm.md"
    echo "🎯 Launching PM Agent (Project Manager)..."
    ;;
  backend)
    PROMPT_FILE="$AGENTS_DIR/backend.md"
    echo "⚙️  Launching Backend Engineer Agent..."
    ;;
  frontend)
    PROMPT_FILE="$AGENTS_DIR/frontend.md"
    echo "🎨 Launching Frontend Engineer Agent..."
    ;;
  devops)
    PROMPT_FILE="$AGENTS_DIR/devops.md"
    echo "🐳 Launching DevOps Engineer Agent..."
    ;;
  *)
    echo "Error: Unknown agent role '$AGENT_ROLE'"
    echo "Available roles: pm, backend, frontend, devops"
    exit 1
    ;;
esac

if [ ! -f "$PROMPT_FILE" ]; then
  echo "Error: Prompt file not found: $PROMPT_FILE"
  exit 1
fi

SYSTEM_PROMPT=$(cat "$PROMPT_FILE")

echo "Project: $PROJECT_DIR"
echo "Prompt:  $PROMPT_FILE"
echo "---"

exec claude --system-prompt "$SYSTEM_PROMPT" --cwd "$PROJECT_DIR"
