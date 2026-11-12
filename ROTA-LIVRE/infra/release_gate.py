"""Publish only the current main revision with a verified GitHub Actions gate."""

import json
import os
from pathlib import Path
import re
import subprocess
import urllib.error
import urllib.parse
import urllib.request


REPOSITORY = "victoriafpizza/GlobalSolution2026"
GIT_REMOTE = f"https://github.com/{REPOSITORY}.git"
ACTIONS = f"https://api.github.com/repos/{REPOSITORY}/actions"
BRANCH_REF = "refs/heads/main"
GATE_JOB = "Deploy - EC2"
REQUIRED_JOBS = {
    "Gitleaks - Segredos",
    "Semgrep - Analise de codigo",
    "Docker Build e Trivy (api)",
    "Docker Build e Trivy (frontend)",
}
SHA = re.compile(r"[0-9a-f]{40}")
STATE = Path("/var/lib/rota-livre-release-gate/attempt")


def github(path):
    request = urllib.request.Request(
        ACTIONS + path,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "rota-livre-release-gate",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=12) as response:
        return json.load(response)


def current_main():
    output = subprocess.check_output(
        ["git", "ls-remote", "--exit-code", GIT_REMOTE, BRANCH_REF],
        text=True,
        timeout=20,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    )
    commit, ref = output.strip().split("\t")
    if ref != BRANCH_REF or not SHA.fullmatch(commit):
        raise ValueError("Unexpected Git ref")
    return commit


def current_deployment():
    try:
        with urllib.request.urlopen(
            "http://127.0.0.1/deploy-revision.txt", timeout=4
        ) as response:
            revision = response.read(128).decode("ascii", errors="replace").strip()
    except (OSError, TimeoutError):
        return None
    return revision if SHA.fullmatch(revision) else None


def approved(jobs):
    by_name = {job["name"]: job for job in jobs}
    gate = by_name.get(GATE_JOB, {})
    return (
        len(jobs) == len(by_name)
        and gate.get("status") == "in_progress"
        and all(
            by_name.get(name, {}).get("conclusion") == "success"
            for name in REQUIRED_JOBS
        )
    )


def eligible_run(commit):
    query = urllib.parse.urlencode(
        {"event": "push", "branch": "main", "head_sha": commit, "per_page": 10}
    )
    runs = github(f"/workflows/devsecops.yml/runs?{query}")["workflow_runs"]
    for run in runs:
        if (
            run["head_sha"] != commit
            or run["head_branch"] != "main"
            or run["event"] != "push"
            or run["status"] != "in_progress"
            or (run.get("head_repository") or {}).get("full_name") != REPOSITORY
        ):
            continue
        run_id, attempt = int(run["id"]), int(run["run_attempt"])
        jobs = github(
            f"/runs/{run_id}/attempts/{attempt}/jobs?per_page=100"
        )["jobs"]
        if approved(jobs):
            return run_id, attempt
    return None


def main():
    commit = current_main()
    if current_deployment() == commit:
        return
    run = eligible_run(commit)
    if run is None:
        return
    run_id, attempt = run
    marker = f"{run_id}/{attempt}/{commit}\n"
    if STATE.exists() and STATE.read_text(encoding="ascii") == marker:
        return
    temporary = STATE.with_suffix(".tmp")
    temporary.write_text(marker, encoding="ascii")
    temporary.replace(STATE)
    print(f"ROTA_LIVRE_RELEASE_GATE run={run_id} attempt={attempt} commit={commit}",
          flush=True)
    subprocess.run(["/usr/local/sbin/rota-livre-deploy", commit], check=True)


if __name__ == "__main__":
    main()
