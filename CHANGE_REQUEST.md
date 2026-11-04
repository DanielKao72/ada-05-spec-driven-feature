# Change Request

Change ID: CR-002

## Goal
Add optional pagination to the customer listing endpoint, `GET /api/v1/customers`, through the `limit` and `offset` query parameters. Requests that omit both parameters keep their current behavior.

## Requirements Covered
- FR-09 (Customer List Pagination)
- FR-06 (List All Customers: behavior preserved when parameters are omitted)
- AC-13 (Paginated window)
- AC-14 (Backward compatibility)
- AC-15 (Single parameter)
- AC-16 (Offset beyond the total)
- AC-17 (Parameter validation)
- AC-18 (Corrupted storage)
- AC-07 (List All Registered Customers: regression)

The definitions live in `REQUIREMENTS.md` and `SPEC.md`; this document does not redefine them.

## Constraints
- Follow AGENTS.md.
- Use REQUIREMENTS.md and SPEC.md as the source of truth.
- Preserve architecture boundaries, including the pagination responsibilities in ARCHITECTURE.md.
- Do not weaken existing tests.
- Do not add dependencies.
- Do not modify `REQUIREMENTS.md`, `SPEC.md`, `ARCHITECTURE.md`, `TASKS.md`, `AGENTS.md`, `docs/REPO_MAP.md`, `scripts/` or this file during implementation.
- Do not change `GET /api/v1/customers/search` or `POST /api/v1/customers`.
- Out of scope: sorting, paginating search results, returning a total count, and changing the response format.

## Verification
- New API tests cover AC-13 through AC-18, with the AC ID in a comment next to each test.
- Repository and service tests cover the pagination behavior in their own layers, using `tmp_path` fixtures.
- All existing tests pass unchanged, including AC-07 and the corrupted storage tests.
- `README.md` documents the new query parameters, and `docs/tracebility.md` traces FR-09 and CR-002.
- `bash scripts/verify_repo.sh` ends with `VERIFY_REPO: PASS`.

## Human Approval
* **Approved to implement:** YES 
* **Approved by:** Juan Daniel Kao Pech
* **Date:** 03/11/2026
