# RepoPilot – Simple Agent Skill for Docker & CI

RepoPilot is a simple AI Agent Skill built with Codex that automatically ensures a repository contains:

-  A `Dockerfile` (Spring Boot, Maven, Java 17 template)
-  A GitHub Actions CI workflow
-  Docker image build & push to GitHub Container Registry (GHCR)

If the files already exist, the skill checks whether they match the template and updates them if needed.  
All changes are made via Pull Request — never direct commits to `main`.

---

Watch the full demonstration here:
[![Watch the demo](https://img.youtube.com/vi/Tg9N8Uv4Igw/0.jpg)](https://www.youtube.com/watch?v=Tg9N8Uv4Igw)


---



##  What This Skill Does

When executed, RepoPilot:

1. Detects if the repository is a Maven-based Java project (`pom.xml` required).
2. Checks for:
    - `Dockerfile`
    - `.github/workflows/ci-build-and-push.yml`
3. If missing → creates them.
4. If present but different from template → updates them.
5. Opens a Pull Request with a dynamic title based on what changed.

The workflow:
- Builds the project with Maven (Java 17)
- Builds a Docker image
- Tags it as: `git_<first 5 chars of commit SHA>`
- Pushes it to:  
  `ghcr.io/<owner>/<repo>:git_xxxxx`

---

## How It Works

This project uses:

- **OpenAI Codex Agent Skills**
- A custom Python script using `PyGithub`
- PR-based repository automation

The skill lives inside:


Codex automatically discovers and executes it when prompted.

---

## Requirements

- Python 3.11+
- `PyGithub`
- GitHub Personal Access Token (PAT) with:
    - `repo`
    - `workflow`
    - `write:packages` (for GHCR)

Environment variable required:

```bash
export GH_TOKEN=your_token_here
