from pathlib import Path
import pytest

from app.core.exceptions import StorageCorruptedError
from app.repositories.json_customer_repository import JsonCustomerRepository
from app.schemas.customer import Customer


def test_repository_creates_missing_file(tmp_path: Path) -> None:
    db_file = tmp_path / "subdir" / "customers.json"
    repo = JsonCustomerRepository(db_file)
    assert db_file.exists()
    assert repo.get_all() == []


def test_repository_save_and_retrieve(tmp_path: Path) -> None:
    db_file = tmp_path / "customers.json"
    repo = JsonCustomerRepository(db_file)
    customer = Customer(name="Alice Johnson", email="alice@example.com")
    repo.save(customer)

    all_records = repo.get_all()
    assert len(all_records) == 1
    assert all_records[0].id == customer.id
    assert all_records[0].name == "Alice Johnson"
    assert all_records[0].email == "alice@example.com"


def test_repository_get_by_id_and_email(tmp_path: Path) -> None:
    db_file = tmp_path / "customers.json"
    repo = JsonCustomerRepository(db_file)
    customer1 = Customer(name="Alice Johnson", email="alice@example.com")
    customer2 = Customer(name="Bob Smith", email="bob@smith.org")
    repo.save(customer1)
    repo.save(customer2)

    assert repo.get_by_id(customer1.id) == customer1
    assert repo.get_by_id(customer2.id) == customer2
    assert repo.get_by_id("nonexistent-id") is None

    assert repo.get_by_email("ALICE@EXAMPLE.COM") == customer1
    assert repo.get_by_email("bob@smith.org") == customer2
    assert repo.get_by_email("unknown@nowhere.com") is None


def test_repository_search_partial_and_case_insensitive(tmp_path: Path) -> None:
    db_file = tmp_path / "customers.json"
    repo = JsonCustomerRepository(db_file)
    c1 = Customer(name="Alexander Hamilton", email="hamilton@treasury.gov")
    c2 = Customer(name="Sarah Connor", email="sarah@cyberdyne.io")
    c3 = Customer(name="George Washington", email="george@mountvernon.org")
    repo.save(c1)
    repo.save(c2)
    repo.save(c3)

    # Search by partial name prefix, infix, suffix
    assert repo.search("alex") == [c1]
    assert repo.search("xand") == [c1]
    assert repo.search("ton") == [c1, c3]  # "Hamilton" and "Washington"

    # Search by partial email
    assert repo.search("cyberdyne") == [c2]
    assert repo.search("mountvernon.org") == [c3]

    # Search case-insensitivity
    assert repo.search("SARAH") == [c2]
    assert repo.search("cYbErDyNe") == [c2]

    # Non-matching search
    assert repo.search("nonexistent") == []


def _repo_with_customers(tmp_path: Path, count: int) -> tuple[JsonCustomerRepository, list[Customer]]:
    repo = JsonCustomerRepository(tmp_path / "customers.json")
    customers = [
        Customer(name=f"Customer {number}", email=f"customer{number}@example.com")
        for number in range(1, count + 1)
    ]
    for customer in customers:
        repo.save(customer)
    return repo, customers


# AC-13: limit and offset together select the window in storage order
def test_repository_get_page_window(tmp_path: Path) -> None:
    repo, customers = _repo_with_customers(tmp_path, 5)
    assert repo.get_page(limit=2, offset=1) == customers[1:3]


# AC-15: limit alone returns the first records; a limit past the end returns what remains
def test_repository_get_page_limit_only(tmp_path: Path) -> None:
    repo, customers = _repo_with_customers(tmp_path, 5)
    assert repo.get_page(limit=2) == customers[:2]
    assert repo.get_page(limit=100) == customers


# AC-15: offset alone returns the remaining records
def test_repository_get_page_offset_only(tmp_path: Path) -> None:
    repo, customers = _repo_with_customers(tmp_path, 5)
    assert repo.get_page(offset=3) == customers[3:]


# AC-14: without arguments the page is the full collection
def test_repository_get_page_defaults_match_get_all(tmp_path: Path) -> None:
    repo, customers = _repo_with_customers(tmp_path, 5)
    assert repo.get_page() == customers
    assert repo.get_page() == repo.get_all()


# AC-16: an offset equal to or greater than the total returns an empty list
@pytest.mark.parametrize("offset", [5, 6])
def test_repository_get_page_offset_beyond_total(tmp_path: Path, offset: int) -> None:
    repo, _ = _repo_with_customers(tmp_path, 5)
    assert repo.get_page(limit=2, offset=offset) == []
    assert repo.get_page(offset=offset) == []


# FR-09: empty storage yields an empty page
def test_repository_get_page_empty_storage(tmp_path: Path) -> None:
    repo = JsonCustomerRepository(tmp_path / "customers.json")
    assert repo.get_page(limit=2, offset=1) == []


# AC-18: corrupted storage raises the domain exception and leaves the file unchanged
def test_repository_get_page_raises_on_corrupted_storage(tmp_path: Path) -> None:
    db_file = tmp_path / "customers.json"
    repo = JsonCustomerRepository(db_file)
    db_file.write_bytes(b"{not valid json")
    original_content = db_file.read_bytes()

    with pytest.raises(StorageCorruptedError):
        repo.get_page(limit=2, offset=1)

    assert db_file.read_bytes() == original_content
