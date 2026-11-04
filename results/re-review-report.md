# Re-review Report

## Review Context
* **Change ID:** CR-002
* **Branch:** `ada09/cr-002`
* **Commit reviewed:** `83e4c36d33a2d1c78c06ed4cae9545a5e8d706d7`, as named in `results/verification-report.md`
* **Original review:** `3e21ffc`, in `results/review-report.md`
* **Branch tip when reviewed:** `4672779`. It differs from `83e4c36` only in `results/commits.txt`, `results/pr.diff`, `results/verification-output.txt` and `results/verification-report.md`.
* **Reviewer agent:** Claude Code (`claude-opus-5-5`), acting as reviewer. This session did not implement the fixes.
* **Scope:** the human decisions, new MUST FIX regressions and the file scope of the fix cycle. This is not a full review from scratch.

## Results

| Finding | Human Decision | Re-review Status | Evidence |
|---|---|---|---|
| RF-01 | MODIFIED, SHOULD FIX | RESOLVED | All 13 required queries are pinned in `tests/test_customer_pagination_api.py:126-164` and return the required status and records. `app/` is unchanged. |
| RF-02 (coder part) | MODIFIED, OPTIONAL | RESOLVED | `README.md:44-45` adds the two missing test files. `docs/tracebility.md:14` now says `TS-01..TS-10, TS-17..TS-20`. |
| RF-02 (human part) | MODIFIED, OPTIONAL | RESOLVED | Commit `1f94c7a` changes only `docs/REPO_MAP.md`, one line. The entry at line 32 no longer says "planned, CR-002". |
| RF-03 | DEFERRED | Not evaluated, as instructed | - |
| RF-04 | ACCEPTED, OPTIONAL | RESOLVED | `test_ac13_paginated_response_matches_full_listing_slice` (`:168-181`) and `test_ac17_limit_100_over_101_records` (`:185-193`). |

**New MUST FIX regressions:** none found.

**File scope:** confirmed. `git diff 3e21ffc 83e4c36` changes no production code. The only file it changes among those locked by `CHANGE_REQUEST.md` is `docs/REPO_MAP.md`, through the human change.

## Evidence

### How the evidence was produced
- **Gate on the repository, at `4672779` with a clean tree:** `bash scripts/verify_repo.sh` gave 84 passed, 1 warning, `REPO_CONTRACT: PASS`, `VERIFY_REPO: PASS`, exit 0. Bytecode and the pytest cache were disabled.
- **Exact commit:** on a `git archive` export of `83e4c36` outside the repository, `python -m pytest -q` gave 84 passed, 1 warning. This matches `results/verification-output.txt`, whose first line is the same commit hash.
- **Probes and mutations:** run only on that export or on temporary copies of it. The new test file collects the 15 new cases the coder reported.
- **`results/pr.diff`:** identical to `git diff 31be625 83e4c36 -- . ':!results' ':!images'`, ignoring line endings.
- **Versions:** Python 3.11.0, fastapi 0.138.1, pydantic 2.14.1, pytest 9.1.1, httpx 0.28.1.

### RF-01: pin the current integer parsing
The required action was to change no production code and add API tests for the listed queries. `git rev-parse` gives the same `app` tree hash, `8b129dc`, at `3e21ffc`, `83e4c36` and `4672779`.

Each query below is a parametrized case in the new tests. The Observed column is a probe of the export with 15 stored customers.

| Query | Required | Observed | Case expects |
|---|---|---|---|
| `limit=2.0` | 200 | 200, 2 records | `emails[:2]` |
| `offset=1.0` | 200 | 200, 14 records | `emails[1:]` |
| `limit=1_0` | 200 | 200, 10 records | `emails[:10]` |
| `offset=1_0` | 200 | 200, 5 records | `emails[10:]` |
| `limit=+5` | 200 | 200, 5 records | `emails[:5]` |
| `limit=%205` | 200 | 200, 5 records | `emails[:5]` |
| `limit=5%20` | 200 | 200, 5 records | `emails[:5]` |
| `limit=1.5` | 422 | 422 | 422 |
| `limit=abc` | 422 | 422 | 422 |
| `limit=true` | 422 | 422 | 422 |
| `limit=` (empty) | 422 | 422 | 422 |
| `limit=1e1` | 422 | 422 | 422 |
| `limit=0x10` | 422 | 422 | 422 |

The record counts match the original review's probes. The accepted cases compare the returned emails in order, not only the count.

The tests can fail when the behavior changes:

| Mutation | Tests that failed |
|---|---|
| `limit` accepts only plain digits | The 5 `limit` cases of `test_ac17_lax_integer_forms_return_200_with_expected_records` |
| `offset` accepts only plain digits | The 2 `offset` cases of the same test |
| `limit` accepts `1.5`, `true`, `1e1`, `0x10` | The 4 matching cases of `test_ac17_rejected_integer_forms_return_422`, plus the existing `test_ac17_invalid_parameters_return_422[limit=1.5]` |
| `limit` accepts an empty value | `test_ac17_rejected_integer_forms_return_422[limit=]` |

- **Not mutated:** `limit=abc`. Its new case and an older case both pass, but this run did not show either one failing.
- **Corrected mutations:** the first `offset` mutation had no effect and all 84 tests passed, because it did not change validation. The first empty-value mutation also did not change the result. Both were corrected, and the table shows the corrected runs.

### RF-02: documentation drift
**Coder part**
- **README tree:** `README.md:37-45` lists all seven `tests/test_*.py` modules at `83e4c36`, plus `conftest.py`. It does not list `tests/__init__.py`, which is not a test file.
- **Traceability:** the NFR-03 row has the updated scenario range. `SPEC.md` defines no TS-11 to TS-16, so the split range is correct.
- **Test count:** the row also changes from 69 to 84 tests. This goes beyond the decision's wording, and 84 matches the verified result. The coder's report says the human approved it during planning, and this review found no other record of that approval.

**Human part**
- **Change:** `1f94c7a` replaces `tests/test_customer_pagination_api.py (planned, CR-002)` with the path in backticks, which also brings it under the contract's doc path check. The file exists.
- **Separate commit:** it is the only file in the commit, and no other commit in the range touches it.
- **Limit of this evidence:** all commits in the range have the same git author, so git history cannot show who wrote which one. That this was the human's change rests on the review request.

### RF-03: deferred
Listed only. Not evaluated, as instructed.

### RF-04: test assertion depth
- **Slice comparison:** `test_ac13_paginated_response_matches_full_listing_slice` asserts `page == full_listing[1:3]`, which compares every field of both records. It also asserts the field names `id`, `name`, `email` and `created_at`.
- **Upper limit:** `test_ac17_limit_100_over_101_records` stores 101 records, requests `limit=100` and asserts the first 100 emails in order.

Each test is the only one that detects its mutation:

| Mutation, applied only to paginated requests | Result |
|---|---|
| Drop `created_at` | 1 failed: the slice test |
| Change `name` to uppercase | 1 failed: the slice test |
| Cap the page at 99 records | 1 failed: the `limit=100` test |

### File scope
Non-evidence changes in `git diff 3e21ffc 83e4c36`:

| File | Lines | Commit |
|---|---|---|
| `README.md` | +3/-1 | `83e4c36` |
| `docs/REPO_MAP.md` | +1/-1 | `1f94c7a` (human change) |
| `docs/tracebility.md` | +1/-1 | `83e4c36` |
| `tests/test_customer_pagination_api.py` | +73/-0 | `83e4c36` |

- **Production code:** `app/` and `requirements.txt` have no diff. `git log 3e21ffc..83e4c36` lists no commit touching them or `.github/`, so nothing was changed and then reverted.
- **Locked files:** `REQUIREMENTS.md`, `SPEC.md`, `ARCHITECTURE.md`, `TASKS.md`, `AGENTS.md`, `scripts/` and `CHANGE_REQUEST.md` have no diff and no commit in the range.
- **Other changes in the diff:** the rest is `results/` and `images/`, which `CHANGE_REQUEST.md` does not lock.
- **Existing tests:** the range removes no test lines.

## New Findings
No new MUST FIX regression was found. Production code is unchanged, the only test change is added lines, and the full suite passes. The new tests use the existing `client` and `test_repo` fixtures, so they stay on `tmp_path` storage.

No new findings are raised at other severities.

## Notes for the Human
These are not findings, and none requires a change under the current decisions.

1. **Meaning of `limit=+5`.** The test sends a raw `+`, which reaches the application as `' 5'`, so it pins the same parsing path as `limit=%205`. A literal plus, `limit=%2B5`, also returned 200 with 5 records in a probe, but no test pins it and the decision does not list it. The coder disclosed the first point.
2. **Commit messages.** `dcc0851` is titled "fix: address ADA-09 review findings" but changes only `results/coder-report.md`. The test and documentation changes are in `83e4c36`, titled "docs:". This does not affect the code.
3. **Human Gate.** `results/human-review-decisions.md` still has "Return to coder-agent" checked. It may need updating as the process advances.
4. **`docs/REPO_MAP.md` tests table.** It does not list `tests/test_corrupted_storage.py`. The decision asked only for the entry that was updated, so this is outside RF-02.

## Limits of This Re-review
- **CI:** the `.github/workflows/verify.yml` result was not inspected.
- **Runtime:** behavior was observed through TestClient only, with no live Uvicorn server.
- **Mutations:** chosen by the reviewer, targeted at the new tests, and not exhaustive.
- **Lint and security:** neither is configured, and no security audit was performed.
- **Effect of this report on the guard:** this file is uncommitted under the protected `results/` path. `scripts/check_repo_contract.py` therefore reports `REPO_CONTRACT: FAIL`, and `scripts/verify_repo.sh` will fail, until the human commits or otherwise handles it. The PASS above was recorded before this file existed.

This report is not a merge approval.
