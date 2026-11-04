# Independent Review Report
## Review Context
* **Change ID:** CR-002

* **Branch / PR:** `ada09/cr-002`, 

* **PR target:** `ada08-after` (`results/run-context.md`)

* **Commit reviewed:** `3e21ffc6ec5e52c4846d2468bbeba8f226da4554`, as named in `results/verification-report.md`. The branch tip is `a2eb747`, which changes only `images/` and `results/`. `app/` and `tests/` are identical at both commits (`git diff 3e21ffc a2eb747 -- . ':!results' ':!images'` is empty).

* **Reviewer agent:** Claude Code, acting as independent reviewer. This session did not implement the change. `results/coder-report.md` does not name the coder's model or session, so independence can only be stated from this session's side.

* **Model:** `claude-opus-5-5`

* **Tools / permissions:**
    - Read, Grep and Glob on the repository.
    - Read-only git: `log`, `show`, `diff`, `grep`, `status`, `rev-parse`, `branch`, `archive`.
    - `bash scripts/verify_repo.sh`, run in the repository with bytecode and pytest cache disabled.
    - Python probes and mutation runs, only on a `git archive` export of `3e21ffc` in a temporary directory outside the repository.
    - Write access used in the repository only for `results/review-contract.md` and this report.

* **Contract order:** the contract text was fixed in the session plan file before the diff was opened. Plan mode blocked repository writes at that point, so `results/review-contract.md` was written to disk later, after approval of the plan, with its text unchanged.

## Requirements Reviewed
| Requirement | Result | Evidence |
|---|---|---|
| FR-09 / AC-13 window | Met | `app/repositories/json_customer_repository.py:52-56`; `test_ac13_paginated_window` |
| FR-06, AC-07, AC-14 no parameters | Met | `test_ts09_list_all_customers` unchanged; `test_ac14_*`, including 101 records with no implicit cap |
| AC-15 single parameter | Met | `test_ac15_limit_only`, `test_ac15_offset_only` |
| AC-16 offset beyond total | Met at realistic sizes | `test_ac16_*` with 5, 6 and 10^20. See Missing Evidence for a 5000-digit offset |
| AC-17 validation | Listed cases met; meaning of "non-integer" is open | `test_ac17_*` and probes. See RF-01 |
| AC-18 corrupted storage | Met | Probe: 500, body `{"detail":"Internal server error."}`, file bytes unchanged |
| TS-17 to TS-20 | Covered | `tests/test_customer_pagination_api.py` |
| CR verification: AC ID comments, layer tests with `tmp_path`, README, traceability | Met | `results/pr.diff` |

Other contract checks:
- **Called APIs and dependencies:** all exist. This covers `get_page`, `get_all_customers(limit, offset)`, `StorageCorruptedError`, its handler in `app/main.py`, the `client` and `test_repo` fixtures, and `file_path`. `requirements.txt` is unchanged.
- **Architecture:** the router validates (`app/routers/customer_router.py:74-85`), the service delegates (`app/services/customer_service.py:34`), and the repository slices. There is no HTTP code in the repository and no file I/O in the router. Signatures match `ARCHITECTURE.md`; `Optional[int]` is equivalent to `int | None`.
- **Protected documents:** `results/pr.diff` does not change `REQUIREMENTS.md`, `SPEC.md` or `CHANGE_REQUEST.md`, nor `ARCHITECTURE.md`, `TASKS.md`, `AGENTS.md`, `docs/REPO_MAP.md` or `scripts/`.
- **Regression:** the only router hunks are the import and the list endpoint, so search and POST are unchanged. The only line removed from existing tests is an import that was extended.

Assessed, no finding:
- `get_page` has no guard against a negative `offset`. `ARCHITECTURE.md` assigns bounds to the router, and the router is the only production caller.
- `get_page` reads the whole file on each request, which assumption A-01 accepts.
- `test_service_delegates_pagination_to_repository` uses a spy, but real-storage service tests sit beside it, so it does not mask behavior.

## Verification Evidence Reviewed
- `results/verification-report.md`: overall gate PASS, based on two screenshots.
- `images/test_evidence.png` and `images/repo_contract_evidence.png`: both show 69 passed and the second shows `VERIFY_REPO: PASS`. Neither shows a commit hash.
- `results/pr.diff`: identical to `git diff 31be625 3e21ffc`, ignoring line endings.
- `results/spec-changes.diff`: identical to `git diff fe80603 31be625`, ignoring line endings.
- `results/commits.txt`: matches the log up to `3e21ffc`. It does not list `a2eb747`, the commit that added it.
- `results/coder-report.md`: the count of 33 new test cases and the AC mapping were recomputed and are correct.

Reviewer reproduction:
- `bash scripts/verify_repo.sh` at `a2eb747`, with a clean tree before `results/review-contract.md` was created: 69 passed, 1 warning, `REPO_CONTRACT: PASS`, `VERIFY_REPO: PASS`, exit 0.
- Installed versions match the report: Python 3.11.0, fastapi 0.138.1, pydantic 2.14.1, pytest 9.1.1, httpx 0.28.1, uvicorn 0.49.0.
- Mutation check, to test the suite beyond green results: 19 single mutations were applied to the export, covering router bounds and defaults, dropped or swapped arguments, slicing in the service, slice errors, reversed order, and treating corrupted storage as empty. The suite failed on all 19.
- The mutation list was chosen by the reviewer and is not exhaustive.

## Findings
### RF-01 - SHOULD FIX
Category: Requirement clarity / test coverage

Requirement / AC: FR-09 Measure, AC-17, TS-19 ("non-integer")

File / Line: `app/routers/customer_router.py:74-85`; `tests/test_customer_pagination_api.py:97-112`

Evidence: TestClient probes against `3e21ffc` with 15 stored customers:

| Query | Status | Records returned |
|---|---|---|
| `limit=2.0` | 200 | 2 |
| `offset=1.0` | 200 | 14 |
| `limit=1_0` | 200 | 10 |
| `offset=1_0` | 200 | 5 |
| `limit=+5` | 200 | 5 |
| `limit=%205` | 200 | 5 |
| `limit=5%20` | 200 | 5 |
| `limit=1.5`, `abc`, `true`, empty, `1e1`, `0x10` | 422 | none |

The invalid-value test only uses `abc` and `1.5` as non-integer inputs. `results/coder-report.md` says the human saw this behavior in the plan and approved it. A search of `CHANGE_REQUEST.md`, `AI_USAGE_LOG.md` and the other versioned documents found no record of that decision outside the coder report.

Problem: The API accepts forms such as `1_0` and `2.0` that a client might reasonably call non-integer, and the specification does not settle it. FR-09 and AC-17 say "non-integer" without defining it, while the SPEC Error Handling section ties 422 to failing Pydantic validation, and these forms pass it. This report therefore does not classify the behavior as a requirement violation. If the human reads "non-integer" as the literal text form, it becomes a MUST FIX.

Risk: The public contract is decided by Pydantic's lax parsing rather than by the specification. No test pins it, so a framework upgrade could change it unnoticed. For example, `limit=1_0` returning 10 records may surprise a client. The only record of the decision is the coder's own statement.

Recommended next step: The human decides and records the interpretation. If lax parsing is accepted, record the decision and add tests that pin it. If strict integers are required, add a failing test first and have the coder implement it. Either way, the Coder agent makes the change, not this review.

### RF-02 - OPTIONAL
Category: Documentation drift

Requirement / AC: AGENTS.md Change Rules; no AC affected

File / Line: `docs/REPO_MAP.md:32`; `README.md:37-43`; `docs/tracebility.md:14`

Evidence:
- `docs/REPO_MAP.md:32` still says "planned, CR-002" for a test file that now exists.
- The README project tree does not list `tests/test_customer_pagination_api.py`. It already omitted `test_corrupted_storage.py`.
- The NFR-03 traceability row has the new count of 69 tests but still says `TS-01..TS-10`.

Problem: These documents no longer fully describe the repository. The coder could not fix `docs/REPO_MAP.md`, because CHANGE_REQUEST.md locks it during implementation, and disclosed that and the README omission.

Risk: Low. A later agent could be misled about what exists.

Recommended next step: The human decides whether to update these in a follow-up change.

### RF-03 - OPTIONAL
Category: Change history clarity

Requirement / AC: None; audit trail

File / Line: Commit `a2eb747`

Evidence: Its message says "Implement pagination", "Updated `CHANGE_REQUEST.md`" and "Created new tests". `git show --stat a2eb747` lists only `images/*.png`, `results/commits.txt`, `results/pr.diff`, `results/run-context.md`, `results/spec-changes.diff` and `results/verification-report.md`. The `results/run-context.md` change only adds bullets.

Problem: The message describes work that is in other commits, not this one.

Risk: Low. Someone reading the history could conclude that code changed after the verified commit, when it did not.

Recommended next step: The human decides whether to reword the commit before merge or leave it and rely on this note.

### RF-04 - OPTIONAL
Category: Test assertion depth

Requirement / AC: FR-09 ("same JSON array format as FR-06"), AC-17 boundary

File / Line: `tests/test_customer_pagination_api.py:23-24`, `:117-120`

Evidence: `emails_in` reduces paginated API responses to their emails, so no paginated API test asserts the other fields. `test_ac17_boundary_parameters_return_200` checks only the status code, on empty storage. No API test requests `limit=100` with more than 100 records. Reviewer probes found the behavior correct: `limit=2&offset=1` equals the matching full-list records, field for field.

Problem: The format requirement holds because both paths share one `response_model`, but no paginated test asserts it. This is a gap in assertions, not a defect in behavior.

Risk: Low. A later change to the paginated response shape would be caught less directly.

Recommended next step: Optionally add one test comparing a paginated response to the matching slice of the full listing, and one with `limit=100` over 101 records.

## Missing Evidence / Open Questions
1. **Commit binding of the screenshots.** They show no commit hash, so they cannot alone tie the PASS to `3e21ffc`. The reviewer's run covers this gap for code and tests only, because those are identical at `3e21ffc` and `a2eb747`. Capturing text output with `git rev-parse HEAD` would be stronger evidence.
2. **Not independently run.** No live Uvicorn server and no CI run were inspected. Runtime behavior was observed through TestClient only. Please inspect the `.github/workflows/verify.yml` result on the PR.
3. **Lint and security checks** are not configured, so there is no evidence from them. The reviewer did not perform a dedicated security audit.
4. **Very large offsets.** `offset` with 5000 digits returned 422, while AC-16 says a greater `offset` returns `[]`. `10**20` works and is tested. This looks like a parser size limit and has little practical impact, so it is noted for the human and not raised as a finding. The exact threshold was not measured.
5. **Repeated parameters.** `limit=2&limit=3` uses the last value (3 records). The specification does not address this, so it is not a finding.
6. **Pre-existing, outside CR-002.** Storage holding valid JSON with a malformed record returned plain-text `Internal Server Error` in a probe with exception re-raising disabled, because `get_all` does not handle Pydantic's validation error. This line is unchanged from `31be625` and AC-18 covers only invalid JSON. Whether it meets the SPEC's logging expectation was not assessed.
7. **Protected-path check.** `scripts/check_repo_contract.py` compares against `HEAD`, so at a committed state it does not check the PR's own changes. The file-scope check for this review was done with `git diff --name-only 31be625 3e21ffc`.
8. **Effect of this review on the guard.** `results/review-contract.md` and this report are uncommitted files under the protected `results/` path. Running `scripts/check_repo_contract.py` after writing them gives `REPO_CONTRACT: FAIL`, naming only these two files, so `scripts/verify_repo.sh` will fail until the human commits or otherwise handles them. The failure comes from these files, not from the code.

## Summary
MUST FIX: 0. No findings at this severity.

SHOULD FIX: 1 (RF-01)

OPTIONAL: 3 (RF-02, RF-03, RF-04)

The approved behavior is implemented in the required layers, all listed acceptance cases pass, and no regression was found. This conclusion also rests on code inspection, probes and mutation runs, not only on green tests. The main open item is the human decision on RF-01, which would become MUST FIX under a strict reading of "non-integer".

## Reviewer Recommendation
[ ] NOT READY

[ ] READY AFTER MUST FIX

[x] READY FOR HUMAN REVIEW

This recommendation is not a merge approval.
