from pathlib import Path
import pytest

from app.core.exceptions import CustomerAlreadyExistsError
from app.repositories.json_customer_repository import JsonCustomerRepository
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.services.customer_service import CustomerService


def test_service_create_customer_and_prevent_duplicates(tmp_path: Path) -> None:
    repo = JsonCustomerRepository(tmp_path / "customers.json")
    service = CustomerService(repo)

    create_data = CustomerCreate(name="Bruce Wayne", email="bruce@wayne.corp")
    response = service.create_customer(create_data)

    assert response.id is not None
    assert response.name == "Bruce Wayne"
    assert response.email == "bruce@wayne.corp"

    # Attempting to create duplicate email should raise CustomerAlreadyExistsError
    with pytest.raises(CustomerAlreadyExistsError):
        service.create_customer(CustomerCreate(name="Another Bruce", email="BRUCE@WAYNE.CORP"))


def test_service_search_customers_with_trimming(tmp_path: Path) -> None:
    repo = JsonCustomerRepository(tmp_path / "customers.json")
    service = CustomerService(repo)

    service.create_customer(CustomerCreate(name="Clark Kent", email="clark@dailyplanet.com"))
    service.create_customer(CustomerCreate(name="Diana Prince", email="diana@themyscira.gov"))

    # Search with whitespace padding
    results = service.search_customers("   KENT   ")
    assert len(results) == 1
    assert results[0].name == "Clark Kent"

    # Search email
    results = service.search_customers("themyscira")
    assert len(results) == 1
    assert results[0].name == "Diana Prince"

    # Search non-matching
    assert service.search_customers("gotham") == []


def test_service_get_all_customers(tmp_path: Path) -> None:
    repo = JsonCustomerRepository(tmp_path / "customers.json")
    service = CustomerService(repo)

    assert service.get_all_customers() == []

    service.create_customer(CustomerCreate(name="Barry Allen", email="barry@centralcity.gov"))
    assert len(service.get_all_customers()) == 1


def _service_with_customers(tmp_path: Path, count: int) -> tuple[CustomerService, list[str]]:
    service = CustomerService(JsonCustomerRepository(tmp_path / "customers.json"))
    emails = [f"customer{number}@example.com" for number in range(1, count + 1)]
    for number, email in enumerate(emails, start=1):
        service.create_customer(CustomerCreate(name=f"Customer {number}", email=email))
    return service, emails


# AC-13: the service returns the requested window as response schemas
def test_service_get_all_customers_returns_window(tmp_path: Path) -> None:
    service, emails = _service_with_customers(tmp_path, 5)

    results = service.get_all_customers(limit=2, offset=1)

    assert all(isinstance(result, CustomerResponse) for result in results)
    assert [result.email for result in results] == emails[1:3]


# AC-14: without arguments the service returns every customer
def test_service_get_all_customers_defaults_return_all(tmp_path: Path) -> None:
    service, emails = _service_with_customers(tmp_path, 5)

    assert [result.email for result in service.get_all_customers()] == emails


# FR-09: pagination is delegated to the repository, not sliced in the service
@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({}, {"limit": None, "offset": 0}),
        ({"limit": 2, "offset": 1}, {"limit": 2, "offset": 1}),
    ],
)
def test_service_delegates_pagination_to_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, kwargs: dict, expected: dict
) -> None:
    repo = JsonCustomerRepository(tmp_path / "customers.json")
    calls = []

    def spy_get_page(limit=None, offset=0):
        calls.append({"limit": limit, "offset": offset})
        return []

    monkeypatch.setattr(repo, "get_page", spy_get_page)

    assert CustomerService(repo).get_all_customers(**kwargs) == []
    assert calls == [expected]
