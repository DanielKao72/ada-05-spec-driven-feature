# Coder Agent Report

## Change
Change ID: CR-002
Branch: ada09/cr-002
Base commit: 31be625

## Requirements Covered
- FR-09 (Customer List Pagination)
- FR-06 (List All Customers: behavior preserved when parameters are omitted)
- AC-07, AC-13, AC-14, AC-15, AC-16, AC-17, AC-18

## Implementation Plan
The plan was approved by the human before any file was edited. It follows the pagination responsibilities in `ARCHITECTURE.md`:
1. Router: bind and validate `limit` (optional, 1 to 100) and `offset` (default 0, minimum 0).
2. Service: delegate both parameters to the repository, with no slicing.
3. Repository: add `get_page(limit, offset)`, which calls `get_all()` and slices the result.
4. Tests: add API, repository and service tests.
5. Docs: update `README.md` and `docs/tracebility.md`.

## Files Changed
| File | Change |
|---|---|
| `app/routers/customer_router.py` | Added the `limit` and `offset` query parameters to `GET /api/v1/customers`; updated the summary and description. |
| `app/services/customer_service.py` | `get_all_customers(limit=None, offset=0)` now delegates to `repository.get_page`. |
| `app/repositories/json_customer_repository.py` | Added `get_page`. |
| `tests/test_customer_pagination_api.py` | New file with API acceptance tests. |
| `tests/test_json_customer_repository.py` | Added repository tests and one import. |
| `tests/test_customer_service.py` | Added service tests and extended one import. |
| `README.md` | Section 4 documents the parameters, a paginated example, an offset beyond the total, and a 422 response. |
| `docs/tracebility.md` | Added FR-09 and CR-002 rows, added a regression note to FR-06, and changed the NFR-03 test count from 36 to 69. |
| `results/coder-report.md` | This report. |

## Tests Added / Updated
33 test cases were added, counting each parametrized case: 21 API, 8 repository and 4 service. No existing test was edited or removed. The suite went from 36 to 69 passing tests.

| Criterion | Tests |
|---|---|
| AC-13 | `test_ac13_paginated_window`, `test_repository_get_page_window`, `test_service_get_all_customers_returns_window` |
| AC-14 | `test_ac14_listing_without_parameters_returns_all`, `test_ac14_listing_without_parameters_has_no_implicit_cap`, `test_repository_get_page_defaults_match_get_all`, `test_service_get_all_customers_defaults_return_all` |
| AC-15 | `test_ac15_limit_only`, `test_ac15_offset_only`, `test_repository_get_page_limit_only`, `test_repository_get_page_offset_only` |
| AC-16 | `test_ac16_offset_beyond_total_returns_empty_list`, `test_repository_get_page_offset_beyond_total` |
| AC-17 | `test_ac17_invalid_parameters_return_422`, `test_ac17_boundary_parameters_return_200` |
| AC-18 | `test_ac18_pagination_with_corrupted_storage_returns_500`, `test_repository_get_page_raises_on_corrupted_storage` |
| AC-07 (regression) | Existing `test_ts09_list_all_customers` (unchanged), plus the AC-14 API tests |
| FR-09 (layer responsibilities) | `test_service_delegates_pagination_to_repository`, `test_repository_get_page_empty_storage` |
| CR-002 constraint (search not paginated) | `test_search_ignores_pagination_parameters` |

## Commands Executed
| Command | Result |
|---|---|
| `git log --oneline -3`, `git show --stat --format=%s HEAD`, `git ls-files results tests/test_customer_pagination_api.py` | Read-only inspection before the change |
| `python -m pytest -q` (before the change) | 36 passed, 1 warning |
| Inline `python -c` probe of FastAPI integer parsing, using a throwaway in-memory app | See Known Limitations; no files changed |
| `python -m pytest -q` (after the change) | 69 passed, 1 warning |
| Inline Python request for `GET /api/v1/customers?limit=101` against a temporary repository | 422; the body matches the `README.md` example |
| `bash scripts/verify_repo.sh` | 69 passed, 1 warning; `REPO_CONTRACT: PASS`; `VERIFY_REPO: PASS`; exit code 0 |
| `git status --short`, `git diff --stat` | Read-only check of changed files |

The warning is a `StarletteDeprecationWarning` from `fastapi/testclient.py`. It was already present before this change.

## Verification Result
`bash scripts/verify_repo.sh` ended with `VERIFY_REPO: PASS`. It ran before this report was created and was not run again afterwards, as instructed, because the repository contract fails while `results/` has uncommitted changes.

## Assumptions
- The base commit is recorded as `31be625`, as the human specified. The working tree's HEAD is `1e1dffb`, which only adds `results/run-context.md`.
- The FR-09 and CR-002 rows in `docs/tracebility.md` use the status "Implementado, pendiente de revisión" because independent review has not happened yet.
- Updating the stale NFR-03 test count falls under the rule to update `docs/tracebility.md` when a change affects a requirement.
- `limit` and `offset` use the plain `int` binding, because `ARCHITECTURE.md` assigns this validation to FastAPI and Pydantic.

## Known Limitations
- **Lenient integer parsing (AC-17 edge, for the reviewer and human to assess).** `abc`, `1.5`, `true` and empty values return 422. Pydantic coerces `limit=2.0`, `offset=1.0`, `limit=1_0`, `limit=+5` and a space-padded `limit=%205` to integers, so these return 200. `SPEC.md` does not settle whether these forms count as non-integer values. The human saw this in the plan and approved the plain binding. No test locks this behavior in.
- `get_page` does not reject a negative `offset` or non-positive `limit`; those bounds are enforced only in the router, as `ARCHITECTURE.md` assigns. A direct caller passing a negative `offset` would get Python's slice-from-the-end behavior.
- `get_page` reads and validates the whole JSON file on each request, in line with assumption A-01 in `REQUIREMENTS.md`.
- Behavior was verified through `TestClient`. No live Uvicorn server was started.
- Stale documentation was left as is:
  - `docs/REPO_MAP.md` still marks `tests/test_customer_pagination_api.py` as "planned, CR-002", but that file is closed for this change.
  - The `README.md` project tree does not list the new test file. It already omitted `test_corrupted_storage.py`.

## Self-Check
[x] Scope respected
[x] Existing tests not weakened
[x] No undocumented dependency/API introduced
[x] Ready for independent review

This report is NOT an approval.

## Fix Cycle
Source of the assigned findings: `results/human-review-decisions.md`.

The plan was approved by the human before any file was edited. No production code changed. The sections above describe the original implementation and were left as written. This section supersedes two of their Known Limitations: "No test locks this behavior in" and the `README.md` project tree omissions.

### Findings Addressed
| Finding | Decision | Action taken |
|---|---|---|
| RF-01 | MODIFIED, SHOULD FIX | Added API tests that pin the current integer parsing, using the human's interpretation of "non-integer" as a value that Pydantic's integer parsing rejects. |
| RF-02 (coder part) | MODIFIED, OPTIONAL | Added the two missing test files to the `README.md` project tree and updated the scenario range in the NFR-03 row of `docs/tracebility.md`. |
| RF-04 | ACCEPTED, OPTIONAL | Added one API test comparing a paginated response to the matching slice of the full listing, and one requesting `limit=100` over 101 stored records. |

Not acted on, as instructed: RF-03, the open items, and the human part of RF-02.

### Files Changed
| File | Change |
|---|---|
| `tests/test_customer_pagination_api.py` | Added four test functions (15 test cases). Existing tests were not edited. |
| `README.md` | Added `test_customer_pagination_api.py` and `test_corrupted_storage.py` to the project tree. |
| `docs/tracebility.md` | NFR-03 row: changed `TS-01..TS-10` to `TS-01..TS-10, TS-17..TS-20`, and the test count from 69 to 84. |
| `results/coder-report.md` | This section. |

- The scenario range is not written as `TS-01..TS-20` because `SPEC.md` defines no TS-11 to TS-16.
- The test count change goes beyond the wording of RF-02. The human approved it during planning, because the new tests would otherwise have made the row out of date.

### Tests Added
15 test cases were added, counting each parametrized case. The suite went from 69 to 84 passing tests. All of them passed on their first run against the unchanged production code.

| Finding | Criterion | Test | Cases |
|---|---|---|---|
| RF-01 | AC-17, TS-19 | `test_ac17_lax_integer_forms_return_200_with_expected_records` (`limit=2.0`, `offset=1.0`, `limit=1_0`, `offset=1_0`, `limit=+5`, `limit=%205`, `limit=5%20`) | 7 |
| RF-01 | AC-17, TS-19 | `test_ac17_rejected_integer_forms_return_422` (`limit=1.5`, `limit=abc`, `limit=true`, empty `limit`, `limit=1e1`, `limit=0x10`) | 6 |
| RF-04 | AC-13, FR-09 | `test_ac13_paginated_response_matches_full_listing_slice` | 1 |
| RF-04 | AC-17, TS-19 | `test_ac17_limit_100_over_101_records` | 1 |

- `limit=abc` and `limit=1.5` are also in the existing `test_ac17_invalid_parameters_return_422`. They are repeated because the decision lists them, and the existing test was left unchanged.
- Queries are sent in the raw URL. `limit=+5` reaches the server with `+` decoded as a space, so it pins the same parsing path as `limit=%205`, not a literal plus sign.

### Commands Executed
| Command | Result |
|---|---|
| `python -m pytest -q tests/test_customer_pagination_api.py` | 36 passed, 1 warning |
| `bash scripts/verify_repo.sh` | 84 passed, 1 warning; `REPO_CONTRACT: PASS`; `VERIFY_REPO: PASS`; exit code 0 |
| `git status --short`, `git diff --name-only`, `git diff --stat`, `git rev-parse HEAD` | Read-only check. Changed files were `README.md`, `docs/tracebility.md` and `tests/test_customer_pagination_api.py`; HEAD was `3c1d004baa28bc446820b559625768d2151257c6` |
| Inline `python -B -c` probe of `/p?limit=+5`, using a throwaway in-memory app, run after verification | The raw query is `limit=+5` and the decoded value is `' 5'`; no repository files changed |

The warning is the same `StarletteDeprecationWarning` recorded above.

### Verification Result
`bash scripts/verify_repo.sh` ended with `VERIFY_REPO: PASS`. It ran on HEAD `3c1d004` with the three changed files above uncommitted, before this section was written. It was not run again afterwards, as instructed, because the repository contract fails while `results/` has uncommitted changes.

This Fix Cycle section is NOT an approval. The findings stay open until the human decides on them.
