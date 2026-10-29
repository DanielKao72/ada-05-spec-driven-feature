# Readiness Improvement Report

## Summary
| | BEFORE | AFTER |
|---|---:|---:|
| Readiness score | 49 / 100 | 83 / 100 |
| Delta | | **+34** |
| Branch | `ada08-before` | `ada08-after` |
| Starting point | `ada08-baseline-v1` (`3fef64c`) | `ada08-baseline-v1` (`3fef64c`) + readiness improvements (`385f58c`) |
| Task / prompt | `TASK_UNDER_TEST.md` (CR-001), official ADA-08 prompt | Same task, same prompt |


## Indicator Comparison
| Indicator | BEFORE | AFTER |
|---|---|---|
| Clarification questions | 0 | 0 |
| Permission requests | 7 | 6 (no `git stash`) |
| Failed / unknown commands | 0 failed; test command inferred (`python -m pytest` vs. README `pytest -v`) | 0 failed; only documented commands used (`python -m pytest -q`, `bash scripts/verify_repo.sh`) |
| Incorrect assumptions | 0 functional; documentation scope and 500 body chosen without a source | 0 functional; documentation scope taken from AGENTS.md rule; 500 body still chosen without a source |
| Out-of-scope files modified | `README.md` (ambiguous, no rule) | 0 (README and traceability required by AGENTS.md) |
| State-altering git commands | `git stash` / `git stash pop` (not governed by any rule) | None (respected AGENTS.md git rule) |
| Validations executed correctly | `pytest` before/after (27 → 35 passed); tests run against original code via `git stash` | `pytest` before (27); new tests (9 passed); `verify_repo.sh` → 36 passed, `REPO_CONTRACT: PASS`, `VERIFY_REPO: PASS` |
| AC → test mapping | Partial (6 of 8 tests under an AC comment; 2 extra tests without one) | Complete (every test annotated with its `CR-001-AC-xx`) |
| Final result | PASS | PASS |
| Qualitative observation | Correct fix, but the agent decided scope, commands and git usage on its own. | Same quality of fix; every process decision is traceable to a repository rule. |
| Discoverability | Agent had to infer the test command, which docs to update and whether git operations were acceptable. | Agent cited `AGENTS.md`, `docs/REPO_MAP.md` and `scripts/verify_repo.sh`; nothing had to be inferred. |
| Implicit knowledge | `results/implicit-knowledge.md`: IK-01, IK-02, IK-03 detected. | All three made explicit or executable (see mapping below). |
| Improvement classification | n/a | Context, Navigation, Executable Knowledge, Guardrail, CI Check (see Changes Made). |
| CI / shared checks | None | `.github/workflows/verify.yml` runs the same `scripts/verify_repo.sh` used by humans and agents. |

Both runs produced a correct fix (PASS). The difference is not the outcome but the uncertainty and the evidence: in AFTER the agent followed a documented process, used the official verification contract and produced a complete AC → test mapping.

## Changes Made

### Improvement I-01
* **Category:** Context
* **Problem:** `AGENTS.md` had no sources of truth, standard commands, protected paths, git rules or stop conditions (BEFORE friction #2; IK-01, IK-02, IK-03).
* **Change:** Rewrote `AGENTS.md` with Read First, Sources of Truth, Repository Map, Standard Commands, Change Rules (documentation and git), Stop Conditions and Definition of Done.
* **Evidence:** The AFTER agent applied the documentation rule, refused `git stash` citing the git rule and annotated every test with its AC ID as required by the DoD.

### Improvement I-02
* **Category:** Context
* **Problem:** No tool-specific entry point for Claude Code.
* **Change:** Added `CLAUDE.md` as a thin adapter that points to `AGENTS.md`, asks for a short plan and requires `verify_repo.sh`; it duplicates no requirements.
* **Evidence:** The AFTER agent ran `bash scripts/verify_repo.sh` as its final validation.

### Improvement I-03
* **Category:** Navigation
* **Problem:** No map of where to change what; protected paths undocumented (BEFORE friction #2).
* **Change:** Added `docs/REPO_MAP.md` with entry points, layer boundaries, test inventory, change guide per change type and Do Not Edit Directly list.
* **Evidence:** The AFTER agent referenced the layer rules and changed exactly the repository, exceptions and app layers listed in the storage change guide.

### Improvement I-04
* **Category:** Executable Knowledge
* **Problem:** No single verification command; test command inconsistent between README and actual usage (BEFORE friction #1; IK-01).
* **Change:** Added `scripts/verify_repo.sh` (tests + repository contract) and pointed `README.md` to it. Added `.gitattributes` so the script keeps LF line endings on Windows.
* **Evidence:** `bash scripts/verify_repo.sh` → `VERIFY_REPO: PASS` in the AFTER run and in the independent human re-run.

### Improvement I-05
* **Category:** Guardrail
* **Problem:** Every rule existed only in natural language (BEFORE friction #1; IK-03).
* **Change:** Added `scripts/check_repo_contract.py` with four deterministic checks: required files, protected paths (human override `ALLOW_PROTECTED_CHANGES=1`), forbidden versioned files (`.env`, keys, `data/*.json`), and paths referenced in agent-facing docs.
* **Evidence:** Appending a line to `SPEC.md` produced `Protected path modified: SPEC.md` and `REPO_CONTRACT: FAIL`; a reference to a missing file was detected during setup.

### Improvement I-06
* **Category:** CI Check
* **Problem:** No validation outside the agent session.
* **Change:** Added `.github/workflows/verify.yml`, which installs dependencies and runs the same `scripts/verify_repo.sh`.
* **Evidence:** The workflow contains no duplicated validation logic; it only calls the shared contract.

## Implicit Knowledge Remediation
| ID | Hidden knowledge | Remediation | Type |
|---|---|---|---|
| IK-01 | Official test/verification command | `AGENTS.md` Standard Commands + `scripts/verify_repo.sh` + CI | Context + Executable Knowledge + CI Check |
| IK-02 | Which documentation must be updated per change | `AGENTS.md` Change Rules + `docs/REPO_MAP.md` Change Guide | Context + Navigation |
| IK-03 | Allowed git operations and protected paths | `AGENTS.md` git rule and Stop Conditions + protected-path check | Context + Guardrail |

IK-01 and IK-03 became executable checks. IK-02 remains documentation only: whether a doc change is "required" cannot be decided deterministically.

## Impact Analysis
- **Biggest impact:** `AGENTS.md` combined with `scripts/verify_repo.sh`. They removed every inferred decision (command, doc scope, git usage) and gave the agent and the human the same definition of done.
- **Guardrail trade-off:** the git rule made the agent safer but removed its way of proving that the tests fail without the fix. A future improvement is a read-only script (for example based on `git archive`) that runs the tests against the baseline without altering the working tree.
- **Human onboarding benefit:** a new developer gets the same entry points, change guide, single verify command and CI check that the agent uses.
- **Still requires human decision:** changes to `REQUIREMENTS.md`/`SPEC.md`, approving protected-path changes, choosing user-facing error messages not defined in SPEC, and judging whether documentation updates are in scope.

## Remaining Gaps
- Lint/formatter not configured; dependencies unpinned; `httpx`/`starlette.testclient` deprecation warning.
- Layer boundaries are documented but not enforced automatically.
- `TASKS.md` does not reference FR/AC IDs; `docs/tracebility.md` is misnamed and in Spanish.
- The protected-path check adds no value in CI (it compares against `HEAD`), and its override is an unaudited environment variable.
- `README.md` project tree does not list `AGENTS.md`, `docs/` or `scripts/`.
