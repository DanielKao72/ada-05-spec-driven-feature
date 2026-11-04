# Review Contract
## Change
CR-002: add optional pagination to `GET /api/v1/customers` via `limit` and `offset` query parameters.
Requests omitting both keep current behavior. Out of scope: sorting, paginating search results, total count,
changing response format, changes to `GET /api/v1/customers/search` or `POST /api/v1/customers`.
Human approval recorded in CHANGE_REQUEST.md (Juan Daniel Kao Pech, 03/11/2026).

## Requirements / Acceptance Criteria
- FR-09: skip first `offset` records in storage order, return at most `limit` of the rest, same JSON array format as FR-06; 200 with exact window (`[]` if offset >= total); 422 when `limit` outside 1..100, `offset` negative, or either non-integer.
- FR-06: without pagination params, 200 with all records (or `[]` if empty).
- SPEC Validation Rule 3: `limit` optional, no default, no upper bound when omitted; `offset` optional, default 0; storage order.
- AC-07: list all stored customers (regression).
- AC-13: 5 stored, `limit=2&offset=1` -> 200, only 2nd and 3rd, storage order.
- AC-14: no params -> 200, JSON array of all stored records.
- AC-15: 5 stored, `limit=2` -> first 2; `offset=3` -> 4th and 5th.
- AC-16: 5 stored, `offset=5` or greater -> 200, `[]`.
- AC-17: `limit` = 0, 101, -1, non-integer -> 422; `offset` = -1, non-integer -> 422; `limit=1` and `limit=100` -> 200.
- AC-18: invalid JSON storage, `limit=2&offset=1` -> 500, file byte-for-byte unchanged.
- CHANGE_REQUEST Verification: API tests for AC-13..18 with AC ID comment next to each test; repository and service tests in their own layers using `tmp_path`; existing tests pass unchanged; README documents the params; `docs/tracebility.md` traces FR-09 and CR-002; `bash scripts/verify_repo.sh` ends `VERIFY_REPO: PASS`.
- SPEC test scenarios: TS-17, TS-18, TS-19, TS-20.

## Architecture Constraints
- Expected dependency flow: Router -> (Deps) -> CustomerService -> JsonCustomerRepository -> JSON file.
- Business-rule location: Router validates `limit`/`offset` bounds. Service delegates pagination parameters and does not slice. Repository does pagination slicing. Interfaces: `get_page(self, limit: int | None = None, offset: int = 0) -> list[Customer]`; `get_all_customers(self, limit: int | None = None, offset: int = 0) -> list[CustomerResponse]`.
- Protected boundaries: no HTTP concerns in repository, no file I/O in router; no new dependencies; no edits to `REQUIREMENTS.md`, `SPEC.md`, `ARCHITECTURE.md`, `TASKS.md`, `AGENTS.md`, `docs/REPO_MAP.md`, `scripts/`, `CHANGE_REQUEST.md`; search and POST endpoints unchanged; corrupted storage returns 500 without exposing stack traces and without altering the file.

## Review Rules
- Verify requirement coverage.
- Verify every called API/dependency exists.
- Check architecture boundaries.
- Inspect tests for masking / false confidence.
- Check regression behavior.
- Identify unnecessary technical debt.
- Cite evidence for every finding.

## Severity
MUST FIX: Requirement violation, regression, security/integrity risk, hallucinated API/dependency, broken architecture constraint, or defect that makes the change unsafe to approve.
SHOULD FIX: Significant maintainability, coverage, design, or clarity issue that does not block the requested behavior.
OPTIONAL: Non-blocking improvement outside the minimum acceptance threshold.
