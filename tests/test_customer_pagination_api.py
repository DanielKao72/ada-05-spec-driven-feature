from pathlib import Path
from typing import List

import pytest
from fastapi.testclient import TestClient

from app.repositories.json_customer_repository import JsonCustomerRepository
from app.schemas.customer import Customer

CUSTOMERS_URL = "/api/v1/customers"


def seed_customers(repo: JsonCustomerRepository, count: int) -> List[str]:
    """Stores `count` customers and returns their emails in storage order."""
    emails = []
    for number in range(1, count + 1):
        email = f"customer{number}@example.com"
        repo.save(Customer(name=f"Customer {number}", email=email))
        emails.append(email)
    return emails


def emails_in(response) -> List[str]:
    return [customer["email"] for customer in response.json()]


# AC-13 / TS-17: limit and offset together return the window in storage order
def test_ac13_paginated_window(client: TestClient, test_repo: JsonCustomerRepository) -> None:
    emails = seed_customers(test_repo, 5)

    response = client.get(f"{CUSTOMERS_URL}?limit=2&offset=1")

    assert response.status_code == 200
    assert emails_in(response) == [emails[1], emails[2]]


# AC-14 / AC-07 / TS-18: omitting both parameters returns all records as a JSON array
def test_ac14_listing_without_parameters_returns_all(
    client: TestClient, test_repo: JsonCustomerRepository
) -> None:
    emails = seed_customers(test_repo, 5)

    response = client.get(CUSTOMERS_URL)

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert emails_in(response) == emails


# AC-14 / AC-07 / TS-18: omitting limit applies no upper bound on the returned records
def test_ac14_listing_without_parameters_has_no_implicit_cap(
    client: TestClient, test_repo: JsonCustomerRepository
) -> None:
    emails = seed_customers(test_repo, 101)

    response = client.get(CUSTOMERS_URL)

    assert response.status_code == 200
    assert emails_in(response) == emails


# AC-15 / TS-17: limit alone returns the first records
def test_ac15_limit_only(client: TestClient, test_repo: JsonCustomerRepository) -> None:
    emails = seed_customers(test_repo, 5)

    response = client.get(f"{CUSTOMERS_URL}?limit=2")

    assert response.status_code == 200
    assert emails_in(response) == emails[:2]


# AC-15 / TS-17: offset alone returns the remaining records
def test_ac15_offset_only(client: TestClient, test_repo: JsonCustomerRepository) -> None:
    emails = seed_customers(test_repo, 5)

    response = client.get(f"{CUSTOMERS_URL}?offset=3")

    assert response.status_code == 200
    assert emails_in(response) == [emails[3], emails[4]]


# AC-16 / TS-18: an offset equal to or greater than the total returns an empty list
@pytest.mark.parametrize("offset", [5, 6, 10**20])
def test_ac16_offset_beyond_total_returns_empty_list(
    client: TestClient, test_repo: JsonCustomerRepository, offset: int
) -> None:
    seed_customers(test_repo, 5)

    response = client.get(f"{CUSTOMERS_URL}?offset={offset}")

    assert response.status_code == 200
    assert response.json() == []


# AC-17 / TS-19: invalid limit or offset values are rejected
@pytest.mark.parametrize(
    "query",
    [
        "limit=0",
        "limit=101",
        "limit=-1",
        "limit=abc",
        "limit=1.5",
        "offset=-1",
        "offset=abc",
        "offset=1.5",
    ],
)
def test_ac17_invalid_parameters_return_422(client: TestClient, query: str) -> None:
    response = client.get(f"{CUSTOMERS_URL}?{query}")

    assert response.status_code == 422


# AC-17 / TS-19: boundary values are accepted
@pytest.mark.parametrize("query", ["limit=1", "limit=100", "offset=0"])
def test_ac17_boundary_parameters_return_200(client: TestClient, query: str) -> None:
    response = client.get(f"{CUSTOMERS_URL}?{query}")

    assert response.status_code == 200


# AC-17 / TS-19: "non-integer" means a value Pydantic's integer parsing rejects
# (results/human-review-decisions.md, RF-01), so these forms are accepted.
# Queries stay in the raw URL: `params=` would encode "+" as %2B and send a different input.
@pytest.mark.parametrize(
    ("query", "expected_slice"),
    [
        ("limit=2.0", slice(2)),
        ("offset=1.0", slice(1, None)),
        ("limit=1_0", slice(10)),
        ("offset=1_0", slice(10, None)),
        ("limit=+5", slice(5)),
        ("limit=%205", slice(5)),
        ("limit=5%20", slice(5)),
    ],
)
def test_ac17_lax_integer_forms_return_200_with_expected_records(
    client: TestClient, test_repo: JsonCustomerRepository, query: str, expected_slice: slice
) -> None:
    emails = seed_customers(test_repo, 15)

    response = client.get(f"{CUSTOMERS_URL}?{query}")

    assert response.status_code == 200
    assert emails_in(response) == emails[expected_slice]


# AC-17 / TS-19: forms that Pydantic's integer parsing rejects return 422 (RF-01)
@pytest.mark.parametrize(
    "query",
    [
        "limit=1.5",
        "limit=abc",
        "limit=true",
        "limit=",
        "limit=1e1",
        "limit=0x10",
    ],
)
def test_ac17_rejected_integer_forms_return_422(client: TestClient, query: str) -> None:
    response = client.get(f"{CUSTOMERS_URL}?{query}")

    assert response.status_code == 422


# AC-13 / FR-09: a paginated response has the same format as the matching slice of the full listing
def test_ac13_paginated_response_matches_full_listing_slice(
    client: TestClient, test_repo: JsonCustomerRepository
) -> None:
    seed_customers(test_repo, 5)
    full_listing = client.get(CUSTOMERS_URL).json()

    response = client.get(f"{CUSTOMERS_URL}?limit=2&offset=1")

    assert response.status_code == 200
    page = response.json()
    assert len(page) == 2
    assert page == full_listing[1:3]
    for customer in page:
        assert set(customer) == {"id", "name", "email", "created_at"}


# AC-17 / TS-19: limit=100 is applied as the upper limit when more records are stored
def test_ac17_limit_100_over_101_records(
    client: TestClient, test_repo: JsonCustomerRepository
) -> None:
    emails = seed_customers(test_repo, 101)

    response = client.get(f"{CUSTOMERS_URL}?limit=100")

    assert response.status_code == 200
    assert emails_in(response) == emails[:100]


# AC-18 / TS-20: a paginated request over invalid JSON returns 500 and leaves the file unchanged
def test_ac18_pagination_with_corrupted_storage_returns_500(
    client: TestClient, test_repo: JsonCustomerRepository
) -> None:
    storage_file: Path = test_repo.file_path
    storage_file.write_bytes(b"{not valid json")
    original_content = storage_file.read_bytes()

    response = client.get(f"{CUSTOMERS_URL}?limit=2&offset=1")

    assert response.status_code == 500
    assert storage_file.read_bytes() == original_content


# CR-002 constraint: search results are not paginated
def test_search_ignores_pagination_parameters(
    client: TestClient, test_repo: JsonCustomerRepository
) -> None:
    emails = seed_customers(test_repo, 3)

    response = client.get(f"{CUSTOMERS_URL}/search?q=customer&limit=1&offset=1")

    assert response.status_code == 200
    assert emails_in(response) == emails
