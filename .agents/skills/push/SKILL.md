---
name: push
description: Create branch, commit, push, and open PR to dev. Supports direct push to dev or branch+PR workflow.
user-invocable: true
---

# Push Workflow

Push changes to the remote repository. Two modes:

## Usage

- `/push` — create a new branch, commit, push, create PR to `dev`, then review the PR
- `/push direct` — commit and push directly to `dev` branch
- `/push <message>` — use the provided message as the commit/PR title

## Steps

### 1. Analyze Changes

- Run `git status` and `git diff` to understand all changes (staged + unstaged + untracked)
- Run `git log dev..HEAD` (if on a branch) to see commits not yet in dev
- If there are no changes to commit, inform the user and stop

### 2. Determine Mode

Parse the arguments:
- `direct` → push directly to dev (Step 2a)
- Anything else or no args → branch + PR workflow (Step 2b)
- If a message was provided (not "direct"), use it as the commit/branch description

### Step 2a: Direct Push to Dev

1. Ensure you're on `dev` branch: `git checkout dev`
2. Stage all relevant changes (be specific — don't `git add .`)
3. Create a commit with a descriptive message based on the changes
4. Push to remote: `git push origin dev`
5. Done — show the commit hash

### Step 2b: Branch + PR Workflow

1. **Generate branch name** from the changes:
   - Format: `<type>/<short-description>` (e.g., `fix/email-verification-security`, `feat/candidate-filters`, `refactor/shared-error-utility`)
   - Types: `feat`, `fix`, `refactor`, `chore`, `docs`, `style`, `perf`, `test`
   - Keep it short, kebab-case, descriptive
2. **Create and switch to the new branch** from current HEAD: `git checkout -b <branch-name>`
3. **Stage all relevant changes** (be specific about which files — don't blindly `git add .`; avoid secrets, .env files, large binaries)
4. **Create a commit** with a descriptive message following conventional commits format
5. **Push the branch**: `git push -u origin <branch-name>`
6. **Create a PR** to `dev` using `gh pr create`:
   - Title: concise description of the changes (under 70 chars)
   - Body: structured with Summary (bullet points of what changed), and Test Plan
   - Base branch: `dev`
7. **Show the PR URL** to the user

### 3. Review the PR (MANDATORY)

**This step is NOT optional. ALWAYS run the review before merging.**

After the PR is created (Step 2b only):
1. Spawn a review agent on the diff (`git diff dev...HEAD`) to catch issues
2. If the review finds critical issues — fix them, commit, and push before proceeding
3. If the review finds only warnings/suggestions — note them but proceed
4. Show the review summary to the user

### 4. Merge (only after review)

- Do NOT merge until the review in Step 3 is complete
- If the user asks to merge, confirm that the review has been done
- If the review was skipped for any reason, run it before merging
- Merge with `gh pr merge --merge`

### Important Rules

- NEVER push secrets, .env files, credentials, or large binaries
- NEVER force push
- NEVER merge without reviewing first — the review step is mandatory
- Always show the user what will be committed before committing (summarize the changes)
- If the user provided a message, use it as the basis for both the commit message and PR title
- The base branch for PRs is always `dev` unless the user specifies otherwise
- After PR creation, return the PR URL so the user can see it
