import os
import sys
from datetime import datetime, timezone
from github import Github, Auth
from github.GithubException import GithubException

WORKFLOW_PATH = ".github/workflows/ci-build-and-push.yml"
DOCKERFILE_PATH = "Dockerfile"

WORKFLOW_YAML = """\
name: CI — build & push image

on:
  push:
    branches: [ "main" ]
  workflow_dispatch:

permissions:
  contents: read
  packages: write

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "17"

      - name: Cache Maven
        uses: actions/cache@v4
        with:
          path: ~/.m2
          key: ${{ runner.os }}-maven-${{ hashFiles('**/pom.xml') }}
          restore-keys: |
            ${{ runner.os }}-maven-

      - name: Build (skip tests)
        run: mvn -B -DskipTests package

      - name: Set Docker image tag
        run: echo "TAG=git_${GITHUB_SHA::5}" >> $GITHUB_ENV

      - name: Compute lowercase image name
        run: |
          echo "IMAGE=ghcr.io/${GITHUB_REPOSITORY,,}" >> $GITHUB_ENV

      - name: Login to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build and push
        uses: docker/build-push-action@v6
        with:
          context: .
          file: ./Dockerfile
          push: true
          tags: |
            ${{ env.IMAGE }}:${{ env.TAG }}
"""

DOCKERFILE = """\
# Dockerfile Java 17 + Maven multi-stage build and test
# Build
FROM maven:3.9.9-eclipse-temurin-17 AS builder
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline -B
COPY src ./src
RUN mvn package -DskipTests -B

# Test
FROM maven:3.9.9-eclipse-temurin-17 AS tester
WORKDIR /app
COPY --from=builder /app /app
RUN mvn test

# Runtime
FROM eclipse-temurin:17-jre-jammy AS runtime
WORKDIR /app
RUN addgroup spring && adduser spring --ingroup spring && mkdir -p /var/log && chown -R spring:spring /var/log
USER spring:spring
COPY --from=builder /app/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java","-jar","/app/app.jar"]
"""

def get_file(repo, path, ref):
    try:
        return repo.get_contents(path, ref=ref)
    except GithubException as e:
        if e.status == 404:
            return None
        raise

def exists(repo, path, ref):
    return get_file(repo, path, ref) is not None

def is_maven_java_repo(repo, ref):
    return exists(repo, "pom.xml", ref)

def create_or_update_file(repo, path, content, branch, commit_message):
    existing = get_file(repo, path, branch)

    if existing:
        current_content = existing.decoded_content.decode("utf-8", errors="replace")
        # Normalize line endings so Windows/macOS don’t cause false diffs
        norm_current = current_content.replace("\r\n", "\n").strip() + "\n"
        norm_new = content.replace("\r\n", "\n").strip() + "\n"

        if norm_current == norm_new:
            print(f"{path}: unchanged")
            return False

        repo.update_file(
            path=path,
            message=commit_message,
            content=content,
            sha=existing.sha,
            branch=branch
        )
        print(f"{path}: updated")
        return True

    repo.create_file(
        path=path,
        message=commit_message,
        content=content,
        branch=branch
    )
    print(f"{path}: created")
    return True



def main():
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    repo_full = os.getenv("GITHUB_REPOSITORY")
    if len(sys.argv) >= 2:
        repo_full = sys.argv[1]

    if not token:
        raise SystemExit("Missing token. Set GH_TOKEN (PAT) or GITHUB_TOKEN.")
    if not repo_full or "/" not in repo_full:
        raise SystemExit("Usage: python agent_bootstrap_ci.py <owner>/<repo>")

    auth = Auth.Token(token)
    gh = Github(auth=auth)
    repo = gh.get_repo(repo_full)
    default_branch = repo.default_branch

    if default_branch != "main":
        print(f"Default branch is '{default_branch}' (not 'main'). Script will still work, workflow triggers main.")
        # You said you use main, so normally this won't happen.

    if not is_maven_java_repo(repo, default_branch):
        print("pom.xml not found at repo root on default branch. Skipping.")
        return

    workflow_exists = exists(repo, WORKFLOW_PATH, default_branch)
    dockerfile_exists = exists(repo, DOCKERFILE_PATH, default_branch)

    print(f"Existing on {default_branch}: workflow={workflow_exists}, dockerfile={dockerfile_exists}")

    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    branch_name = f"agent/bootstrap-ci-{ts}"

    base_ref = repo.get_git_ref(f"heads/{default_branch}")
    repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=base_ref.object.sha)

    docker_changed = create_or_update_file(
        repo, DOCKERFILE_PATH, DOCKERFILE, branch_name,
        "chore: ensure Dockerfile (Java 17)"
    )

    workflow_changed = create_or_update_file(
        repo, WORKFLOW_PATH, WORKFLOW_YAML, branch_name,
        "chore: ensure CI workflow (build & push to GHCR)"
    )

    if not (docker_changed or workflow_changed):
        print("No changes detected vs templates; not opening PR.")
        return

    # ---- Dynamic PR title/body based on what changed ----
    parts = []
    if workflow_changed:
        parts.append("CI workflow")
    if docker_changed:
        parts.append("Dockerfile")

    title = "Update " + " + ".join(parts)

    body_lines = ["This PR updates:"]
    if workflow_changed:
        body_lines.append(f"- `{WORKFLOW_PATH}` (build jar with Maven, build/push image to GHCR)")
    if docker_changed:
        body_lines.append(f"- `{DOCKERFILE_PATH}` (Java 17 multi-stage build)")

    body = "\n".join(body_lines)

    pr = repo.create_pull(
        title=title,
        body=body,
        head=branch_name,
        base=default_branch,
    )

    print(f"Opened PR: {pr.html_url}")


if __name__ == "__main__":
    main()

