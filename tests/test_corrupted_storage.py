import logging
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.exceptions import StorageCorruptedError
from app.repositories.json_customer_repository import JsonCustomerRepository

CORRUPTED_CONTENT = b"{not valid json"


@pytest.fixture
def corrupted_file(test_repo: JsonCustomerRepository) -> Path:
    """Overwrites the isolated test storage file with invalid JSON."""
    test_repo.file_path.write_bytes(CORRUPTED_CONTENT)
    return test_repo.file_path


# CR-001-AC-01: Listing with corrupted storage responds HTTP 500
def test_list_customers_with_corrupted_storage_returns_500(
    client: TestClient, corrupted_file: Path
) -> None:
    response = client.get("/api/v1/customers")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error."}


# CR-001-AC-02: Search with corrupted storage responds HTTP 500
def test_search_customers_with_corrupted_storage_returns_500(
    client: TestClient, corrupted_file: Path
) -> None:
    response = client.get("/api/v1/customers/search?q=ana")
    assert response.status_code == 500


# CR-001-AC-03: Creation responds HTTP 500 and does not overwrite corrupted storage
def test_create_customer_with_corrupted_storage_does_not_overwrite_file(
    client: TestClient, corrupted_file: Path
) -> None:
    original_content = corrupted_file.read_bytes()
    payload = {"name": "Diana Prince", "email": "diana@themyscira.gov"}

    response = client.post("/api/v1/customers", json=payload)

    assert response.status_code == 500
    assert corrupted_file.read_bytes() == original_content


# CR-001-AC-04: An error-level log entry identifies the file path and decode failure
@pytest.mark.parametrize(
    "method, url, body",
    [
        ("GET", "/api/v1/customers", None),
        ("GET", "/api/v1/customers/search?q=ana", None),
        ("POST", "/api/v1/customers", {"name": "Diana Prince", "email": "diana@themyscira.gov"}),
    ],
)
def test_corrupted_storage_emits_error_log(
    client: TestClient,
    corrupted_file: Path,
    caplog: pytest.LogCaptureFixture,
    method: str,
    url: str,
    body: dict | None,
) -> None:
    with caplog.at_level(logging.ERROR, logger="app.repositories.json_customer_repository"):
        client.request(method, url, json=body)

    error_records = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert error_records, "Expected an error-level log entry"
    message = error_records[0].getMessage()
    assert str(corrupted_file) in message
    assert "decode" in message.lower()


# CR-001-AC-04: Repository propagates the decode failure as a domain exception
def test_repository_raises_on_corrupted_storage(corrupted_file: Path) -> None:
    repo = JsonCustomerRepository(corrupted_file)
    with pytest.raises(StorageCorruptedError):
        repo.get_all()
    assert corrupted_file.read_bytes() == CORRUPTED_CONTENT


# CR-001-AC-05: An empty storage file is still treated as an empty list
def test_empty_storage_file_is_treated_as_empty_list(
    client: TestClient, test_repo: JsonCustomerRepository
) -> None:
    test_repo.file_path.write_text("", encoding="utf-8")

    assert client.get("/api/v1/customers").json() == []
    assert client.get("/api/v1/customers/search?q=ana").json() == []

    response = client.post(
        "/api/v1/customers", json={"name": "Diana Prince", "email": "diana@themyscira.gov"}
    )
    assert response.status_code == 201
    assert len(test_repo.get_all()) == 1


# CR-001-AC-05: A missing storage file is still initialized with [] (TS-10)
def test_missing_storage_file_is_initialized(tmp_path: Path) -> None:
    db_file = tmp_path / "missing" / "customers.json"
    repo = JsonCustomerRepository(db_file)
    db_file.unlink()

    assert repo.get_all() == []
    assert db_file.read_text(encoding="utf-8") == "[]"
