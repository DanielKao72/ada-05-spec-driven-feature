# Task Under Test

Change ID: CR-001

## Goal

Fix the handling of a corrupted JSON storage file. Currently `JsonCustomerRepository._read_raw_data` (`app/repositories/json_customer_repository.py`) catches `json.JSONDecodeError` and silently returns `[]`. As a result:

1. `GET /api/v1/customers` and `GET /api/v1/customers/search` respond `200 OK` with `[]`, hiding the read failure.
2. `POST /api/v1/customers` reads `[]`, appends the new customer, and overwrites the file, losing every record that existed in the corrupted file.

The change must make a corrupted JSON read propagate as an error, so that the API responds with HTTP 500 and descriptive server-side logging, and the storage file is not overwritten.

## Requirements Covered

- NFR-01 (Local JSON Persistence: safe read/write operations)
- SPEC.md › Error Handling: "HTTP 500 Internal Server Error ... corrupted JSON data, accompanied by descriptive server-side logging"
- FR-05, FR-06 (creation and listing behavior when storage is corrupted)

## Acceptance Criteria

These criteria are derived from SPEC.md › Error Handling and NFR-01; they do not introduce new requirements.

### CR-001-AC-01: Listing with Corrupted Storage
* **Given** the JSON storage file contains invalid JSON (e.g. `{not valid json`),
* **When** a client requests `GET /api/v1/customers`,
* **Then** the API responds with HTTP 500 Internal Server Error instead of `200 OK` with `[]`.

### CR-001-AC-02: Search with Corrupted Storage
* **Given** the JSON storage file contains invalid JSON,
* **When** a client requests `GET /api/v1/customers/search?q=ana`,
* **Then** the API responds with HTTP 500 Internal Server Error.

### CR-001-AC-03: Creation Does Not Overwrite Corrupted Storage
* **Given** the JSON storage file contains invalid JSON,
* **When** a client requests `POST /api/v1/customers` with a valid payload `{"name": "Diana Prince", "email": "diana@themyscira.gov"}`,
* **Then** the API responds with HTTP 500 Internal Server Error and the file content remains byte-for-byte identical to its content before the request.

### CR-001-AC-04: Server-Side Logging
* **Given** the JSON storage file contains invalid JSON,
* **When** any customer endpoint attempts to read the storage,
* **Then** an error-level log entry is emitted that identifies the storage file path and the JSON decoding failure.

### CR-001-AC-05: Existing Behavior Preserved
* **Given** the JSON storage file is missing or empty,
* **When** a client requests any customer endpoint,
* **Then** the file is initialized (if missing), the storage is treated as an empty list, and AC-01 through AC-07 from SPEC.md continue to pass.

## Verification

New `pytest` tests using `TestClient` and a temporary JSON file (`tmp_path`) containing invalid content (e.g. `{not valid json`):

- `GET /api/v1/customers` responds HTTP 500.
- `GET /api/v1/customers/search?q=ana` responds HTTP 500.
- `POST /api/v1/customers` with a valid payload responds HTTP 500 and the file content remains identical to the original (not overwritten).
- An error entry is emitted to the server log (verifiable with `caplog`).

Regression checks:

- A missing file is still initialized with `[]` (TS-10).
- An empty file is still treated as an empty list.
- The full suite (`pytest -v`) passes with no failures, including AC-01 through AC-07.

## Constraints

- Use REQUIREMENTS.md and SPEC.md as the source of truth.
- Keep changes scoped to this task.
- Do not redefine requirements in this file.
- Do not change the response body format of existing endpoints in success cases.
- Do not add new dependencies (use the standard library `logging` module).
