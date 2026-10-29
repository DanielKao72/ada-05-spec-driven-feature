# Agent Instructions

Operational contract for any coding agent (and human) working in this repository.
This file says where things are and how to work; it does not restate requirements.

## Read First
1. `TASK_UNDER_TEST.md` - the change currently requested (if present).
2. `REQUIREMENTS.md` - functional and non-functional requirements (FR-xx, NFR-xx).
3. `SPEC.md` - verifiable behavior, acceptance criteria (AC-xx), error handling.
4. `ARCHITECTURE.md` - layers, responsibilities, error-handling strategy.
5. `docs/REPO_MAP.md` - where each thing lives, change guide, protected paths.
6. `TASKS.md` - original implementation task breakdown (T-01..T-06).

## Sources of Truth
- Requirements live only in `REQUIREMENTS.md`.
- Verifiable behavior and acceptance criteria live only in `SPEC.md`.
- Layer boundaries live in `ARCHITECTURE.md`.
- `TASK_UNDER_TEST.md` references requirements; it never overrides them.
- Do not change requirements, spec or task files to make tests pass.

## Repository Map
- `app/` - FastAPI application (router -> service -> repository).
- `tests/` - pytest suite with isolated `tmp_path` fixtures.
- `docs/` - repository map and traceability matrix.
- `scripts/` - deterministic verification scripts.
- `results/` - course evidence reports (do not edit unless asked).
- `data/` - runtime JSON storage (not versioned, never edit).

Details: `docs/REPO_MAP.md`.

## Standard Commands
Run every command from the repository root.

| Purpose | Command |
|---|---|
| Install | `python -m pip install -r requirements.txt` |
| Run | `python -m uvicorn app.main:app --reload --port 8000` |
| Test | `python -m pytest -q` |
| Single test file | `python -m pytest -q tests/<file>.py` |
| Lint | Not configured. Do not add a linter without approval. |
| Verify (required before DONE) | `bash scripts/verify_repo.sh` |

`scripts/verify_repo.sh` is the same contract that CI runs (`.github/workflows/verify.yml`).

## Change Rules
- Keep changes scoped to the requested task.
- Put each change in the layer that owns the behavior (see Change Guide in `docs/REPO_MAP.md`).
- Add tests for every new behavior; reuse the fixtures in `tests/conftest.py`.
- Do not delete, skip or weaken existing tests.
- Do not add dependencies without justification and human approval.
- Do not edit protected paths (listed in `docs/REPO_MAP.md`); `scripts/check_repo_contract.py` enforces this.
- Documentation updates:
  - Update `docs/tracebility.md` when a change implements or affects a requirement or change request.
  - Update `README.md` only when the public API contract changes (endpoint, status code, request/response example).
  - Do not edit other documentation unless the task asks for it.
- Git: read-only commands (`status`, `diff`, `log`, `show`) are allowed. Do not run state-altering commands (`stash`, `reset`, `checkout`, `switch`, `restore`, `rebase`, `clean`, `commit`, `push`) unless the human explicitly asks.

## Stop Conditions
Stop and ask for human input when:
- requirements, spec or task conflict or are ambiguous;
- the task seems to require editing a protected path;
- an architecture boundary must change (e.g. HTTP concerns in the repository, file I/O in the router);
- a new dependency is needed;
- a destructive action is required (deleting files, altering git state, touching `data/`);
- `scripts/verify_repo.sh` fails for reasons unrelated to the task.

## Definition of Done
- `bash scripts/verify_repo.sh` ends with `VERIFY_REPO: PASS`.
- Every acceptance criterion referenced by the task is covered by at least one test, with the AC ID in a comment next to the test.
- Only task-related files changed; no protected path changed.
- Documentation updated according to the Change Rules.
- Final report lists: files modified, commands executed with their results, and an AC -> test mapping.
