"""Tests for CR-001: corrupted JSON storage must surface as HTTP 500 without data loss."""

import logging
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.core.exceptions import CustomerStorageError
from app.dependencies import get_customer_repository
from app.main import app
from app.repositories.json_customer_repository import JsonCustomerRepository

CORRUPTED_CONTENT = b"{not valid json"


@pytest.fixture
def corrupted_file(tmp_path: Path) -> Path:
    db_file = tmp_path / "customers.json"
    db_file.write_bytes(CORRUPTED_CONTENT)
    return db_file


@pytest.fixture
def corrupted_client(corrupted_file: Path) -> Generator[TestClient, None, None]:
    repo = JsonCustomerRepository(corrupted_file)
    app.dependency_overrides[get_customer_repository] = lambda: repo
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# CR-001-AC-01
def test_list_with_corrupted_storage_returns_500(corrupted_client: TestClient) -> None:
    response = corrupted_client.get("/api/v1/customers")
    assert response.status_code == 500


# CR-001-AC-02
def test_search_with_corrupted_storage_returns_500(corrupted_client: TestClient) -> None:
    response = corrupted_client.get("/api/v1/customers/search", params={"q": "ana"})
    assert response.status_code == 500


# CR-001-AC-03
def test_create_with_corrupted_storage_returns_500_and_preserves_file(
    corrupted_client: TestClient, corrupted_file: Path
) -> None:
    original = corrupted_file.read_bytes()
    response = corrupted_client.post(
        "/api/v1/customers",
        json={"name": "Diana Prince", "email": "diana@themyscira.gov"},
    )
    assert response.status_code == 500
    assert corrupted_file.read_bytes() == original


# CR-001-AC-04
def test_corrupted_storage_emits_error_log(
    corrupted_client: TestClient, corrupted_file: Path, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.ERROR, logger="app.repositories.json_customer_repository"):
        corrupted_client.get("/api/v1/customers")

    error_records = [r for r in caplog.records if r.levelno == logging.ERROR]
    assert error_records
    message = error_records[0].getMessage()
    assert str(corrupted_file) in message
    assert "JSON" in message


def test_500_response_does_not_expose_internal_details(
    corrupted_client: TestClient, corrupted_file: Path
) -> None:
    response = corrupted_client.get("/api/v1/customers")
    body = response.text
    assert str(corrupted_file) not in body
    assert "Traceback" not in body


def test_repository_raises_storage_error_on_corrupted_file(corrupted_file: Path) -> None:
    repo = JsonCustomerRepository(corrupted_file)
    with pytest.raises(CustomerStorageError):
        repo.get_all()


# CR-001-AC-05 regressions
def test_repository_initializes_missing_file(tmp_path: Path) -> None:
    db_file = tmp_path / "customers.json"
    repo = JsonCustomerRepository(db_file)
    assert db_file.read_text(encoding="utf-8").strip() == "[]"
    assert repo.get_all() == []


def test_empty_file_is_treated_as_empty_list(tmp_path: Path) -> None:
    db_file = tmp_path / "customers.json"
    db_file.write_text("", encoding="utf-8")
    repo = JsonCustomerRepository(db_file)
    assert repo.get_all() == []

    app.dependency_overrides[get_customer_repository] = lambda: repo
    try:
        with TestClient(app) as test_client:
            assert test_client.get("/api/v1/customers").json() == []
            assert test_client.get("/api/v1/customers/search", params={"q": "ana"}).json() == []
    finally:
        app.dependency_overrides.clear()
