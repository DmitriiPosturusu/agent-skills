---
name: bootstrap-gh-actions
description: >
  Use this skill ONLY when the user asks to bootstrap or update CI for a repository:
  - Ensure a Spring Boot (Maven, Java 17) repo has a Dockerfile and a GitHub Actions workflow that builds and pushes to GHCR.
  - It must open a PR (never commit to main directly).
  Do NOT use for non-Java repos.
---

## Goal
Run the repo bootstrap script to create/update:
- Dockerfile (if missing or template changed)
- .github/workflows/ci-build-and-push.yml (if missing or template changed)
  Open a PR with a title that matches the changed files.

## Preconditions
- The target repository is checked out locally.
- Python is available.
- A GitHub token is available in GH_TOKEN or GITHUB_TOKEN with permissions to create branches and PRs.
- For workflow file updates, token needs workflow permissions.

## Procedure
1. Confirm repo looks like Maven Java (pom.xml at root).
2. Run the script:
    - Prefer GH_TOKEN env var.
    - Command: python .agents/skills/bootstrap-gh-actions/scripts/agent_bootstrap_ci.py <owner>/<repo>
3. If the script reports "No changes detected", stop.
4. If a PR URL is produced, return it to the user and summarize what changed.

## Safety
- Never print secrets.
- Never force-push.
- Use PRs only.
