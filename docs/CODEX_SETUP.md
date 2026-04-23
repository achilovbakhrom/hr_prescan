# Codex Setup

This repository already includes `AGENTS.md`, which Codex reads as project instructions.

## Local Codex config

Codex runtime configuration is local to the machine and lives in:

```text
~/.codex/config.toml
```

Add or confirm a project entry like this:

```toml
model = "gpt-5.4"
model_reasoning_effort = "high"
service_tier = "fast"

[projects."/absolute/path/to/hr_prescan"]
trust_level = "trusted"
```

For this machine, the project path is:

```toml
[projects."/Users/bakhromachilov/startups/hr_prescan"]
trust_level = "trusted"
```

## What to commit

- `AGENTS.md` is the repo-level instruction file for Codex.
- `.claude/settings.json` is the repo-level Claude hook config.

Do not commit `~/.codex/config.toml` or `.claude/settings.local.json`; those are local-machine configuration files and can contain secrets or user-specific paths.
