# Repository Map

Answers "where is what I need?". Layer rules come from `ARCHITECTURE.md`.

## Entry Points
| Path | Role |
|---|---|
| `app/main.py` | Application factory: creates the FastAPI app, mounts routers, app-wide configuration (middleware, exception handlers), `/health`. |
| `app/routers/customer_router.py` | HTTP layer: routes under `/api/v1/customers`, query/body binding, status codes. |
| `app/services/customer_service.py` | Business layer: query normalization, uniqueness rules, orchestration. |
| `app/repositories/json_customer_repository.py` | Persistence layer: JSON file read/write, file bootstrap, filtering. |
| `app/schemas/customer.py` | Pydantic models: `Customer`, `CustomerCreate`, `CustomerResponse`. |
| `app/core/exceptions.py` | Domain exceptions shared across layers. |
| `app/core/config.py` | Settings, including the storage path `data/customers.json`. |
| `app/dependencies.py` | Dependency injection providers (repository, service). |

## Layer Boundaries
- Router: HTTP only. No file I/O, no business rules.
- Service: business rules only. No FastAPI/HTTP types.
- Repository: storage only. No `HTTPException`, no HTTP status codes.
- Domain errors cross layers as exceptions defined in `app/core/exceptions.py`.

## Tests
| Path | Covers |
|---|---|
| `tests/conftest.py` | Fixtures: `test_repo` (repository on a `tmp_path` file), `client` (TestClient with the repository overridden). |
| `tests/test_domain_models.py` | Pydantic schema validation. |
| `tests/test_json_customer_repository.py` | Repository unit tests (bootstrap, persistence, search). |
| `tests/test_customer_service.py` | Service unit tests. |
| `tests/test_customer_api_validation.py` | API status codes and validation errors. |
| `tests/test_customer_search_api.py` | Acceptance scenarios AC-01..AC-07 / TS-01..TS-10. |

Tests must never read or write `data/customers.json`; always use `tmp_path`.

## Change Guide
If changing API behavior (routes, status codes, query/body validation):
1. Check `REQUIREMENTS.md` / `SPEC.md`.
2. Update `app/routers/` (or `app/main.py` for app-wide behavior).
3. Update the service only if business behavior changes.
4. Add or modify tests in `tests/test_customer_api_validation.py` or a new `tests/test_*.py`.
5. Update `README.md` (API contract) and `docs/tracebility.md`.
6. Run `bash scripts/verify_repo.sh`.

If changing storage behavior (reading, writing, file errors):
1. Check `SPEC.md` and `ARCHITECTURE.md` (Error Handling).
2. Update `app/repositories/`; add domain exceptions in `app/core/exceptions.py` if needed.
3. Add repository unit tests and, if the HTTP result changes, API tests.
4. Update `docs/tracebility.md`; update `README.md` only if the API contract changes.
5. Run `bash scripts/verify_repo.sh`.

If changing business rules:
1. Check `REQUIREMENTS.md` / `SPEC.md`.
2. Update `app/services/`.
3. Add tests in `tests/test_customer_service.py`.
4. Update `docs/tracebility.md`.
5. Run `bash scripts/verify_repo.sh`.

## Do Not Edit Directly
Enforced by `scripts/check_repo_contract.py` (human override: `ALLOW_PROTECTED_CHANGES=1`).
- `REQUIREMENTS.md`, `SPEC.md` - sources of truth; change only by human decision.
- `TASK_UNDER_TEST.md` - task definition under test.
- `REPOSITORY_READINESS_AUDIT.md`, `results/` - course evidence.
- `scripts/`, `.github/` - verification guardrails.
- `data/` - runtime storage; must never be versioned.
- `.env` and any secret or key file - must never be versioned.

## Verification
- Full contract: `bash scripts/verify_repo.sh`
- Tests only: `python -m pytest -q`
