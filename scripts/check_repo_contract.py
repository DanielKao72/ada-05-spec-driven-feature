"""Deterministic repository readiness checks.

Checks:
1. Essential files exist.
2. No protected path is modified in the working tree (vs. BASE_REF, default HEAD).
3. No runtime data or secret files are versioned.
4. Paths referenced in agent-facing docs exist.

Exit code 0 on PASS, 1 on FAIL.
Set ALLOW_PROTECTED_CHANGES=1 to accept protected-path changes after human approval.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FILES = [
    "AGENTS.md",
    "README.md",
    "REQUIREMENTS.md",
    "SPEC.md",
    "ARCHITECTURE.md",
    "TASKS.md",
    "docs/REPO_MAP.md",
    "scripts/verify_repo.sh",
    "requirements.txt",
    "tests/conftest.py",
]

# Exact files or directory prefixes (ending in "/") that must not change without human approval.
PROTECTED_PATHS = [
    "REQUIREMENTS.md",
    "SPEC.md",
    "TASK_UNDER_TEST.md",
    "REPOSITORY_READINESS_AUDIT.md",
    "results/",
    "scripts/",
    ".github/",
    "data/",
]

# Tracked files that must never be versioned.
FORBIDDEN_TRACKED = [
    re.compile(r"(^|/)\.env(\..+)?$"),
    re.compile(r"\.(pem|key|p12|pfx)$"),
    re.compile(r"(^|/)id_(rsa|ed25519)$"),
    re.compile(r"^data/.+\.json$"),
]

# Paths that may be referenced in docs without existing yet (runtime files, evidence added later).
OPTIONAL_PATHS = {"data/customers.json", ".env", "REPOSITORY_READINESS_AUDIT.md"}

DOCS_TO_CHECK = ["AGENTS.md", "CLAUDE.md", "docs/REPO_MAP.md"]
PATH_TOKEN = re.compile(r"`([A-Za-z0-9_.\-/]+)`")


def git(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def check_required_files() -> list[str]:
    return [f"Missing required file: {path}" for path in REQUIRED_FILES if not (ROOT / path).exists()]


def is_protected(path: str) -> bool:
    return any(path == p or (p.endswith("/") and path.startswith(p)) for p in PROTECTED_PATHS)


def check_protected_paths() -> list[str]:
    if os.environ.get("ALLOW_PROTECTED_CHANGES") == "1":
        print("  protected-path check skipped (ALLOW_PROTECTED_CHANGES=1)")
        return []
    base_ref = os.environ.get("BASE_REF", "HEAD")
    changed = set(git("diff", "--name-only", base_ref))
    changed |= set(git("ls-files", "--others", "--exclude-standard"))
    return [f"Protected path modified: {path}" for path in sorted(changed) if is_protected(path)]


def check_forbidden_tracked() -> list[str]:
    return [
        f"Forbidden file is versioned: {path}"
        for path in git("ls-files")
        if any(pattern.search(path) for pattern in FORBIDDEN_TRACKED)
    ]


def looks_like_path(token: str) -> bool:
    return "/" in token or bool(re.search(r"\.(md|py|sh|yml|yaml|txt|json)$", token))


def check_doc_paths() -> list[str]:
    errors = []
    for doc in DOCS_TO_CHECK:
        doc_path = ROOT / doc
        if not doc_path.exists():
            continue
        for token in PATH_TOKEN.findall(doc_path.read_text(encoding="utf-8")):
            if not looks_like_path(token) or token.startswith("/") or token in OPTIONAL_PATHS:
                continue
            if not (ROOT / token).exists():
                errors.append(f"{doc} references a missing path: {token}")
    return errors


def main() -> int:
    checks = [
        ("required files", check_required_files),
        ("protected paths", check_protected_paths),
        ("forbidden tracked files", check_forbidden_tracked),
        ("doc path references", check_doc_paths),
    ]
    errors = []
    for name, check in checks:
        found = check()
        print(f"  {name}: {'FAIL' if found else 'ok'}")
        errors.extend(found)

    if errors:
        print("REPO_CONTRACT: FAIL")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("REPO_CONTRACT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
