---
name: business-review
description: Review code changes against business logic docs, check consistency, and flag conflicts
user-invocable: true
---

# Business Logic Review

Review the current code changes against the project's business logic documentation and flag any issues.

## Steps

1. **Read the business logic docs**
   - Read `docs/BUSINESS_LOGIC.md` fully
   - Read `AGENTS.md` for project conventions

2. **Identify what changed**
   - Run `git diff` to see staged and unstaged changes
   - Run `git diff --cached` for staged changes
   - Summarize what business logic is affected

3. **Review against business rules**
   For each changed file, check:
   - Does the change align with documented user flows and requirements?
   - Are there any contradictions with existing business rules?
   - Are status transitions valid per the documented state machine?
   - Are permissions/roles respected (HR vs Candidate vs Admin)?
   - Is multi-tenancy preserved (company scoping)?
   - Are edge cases from the docs handled?

4. **Check cross-feature impact**
   - Does this change affect other features (e.g., changing vacancy model affects interviews, applications)?
   - Are API contracts maintained (serializers match frontend types)?
   - Are Celery tasks still triggered correctly?

5. **Report findings**
   Output a clear report:
   - **OK**: Changes that align with business logic
   - **WARNING**: Changes that might conflict or need attention
   - **ISSUE**: Changes that contradict documented business rules
   - **SUGGESTION**: Improvements based on business requirements

6. **Fix issues if found**
   - If there are clear issues, fix them
   - If ambiguous, ask the user before making changes
