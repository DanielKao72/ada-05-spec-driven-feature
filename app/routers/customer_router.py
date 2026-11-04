from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.exceptions import CustomerAlreadyExistsError
from app.dependencies import get_customer_service
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/api/v1/customers", tags=["Customers"])


@router.get(
    "/search",
    response_model=List[CustomerResponse],
    status_code=status.HTTP_200_OK,
    summary="Search customers by partial name or email",
    description="Performs a case-insensitive substring search across customer names and email addresses.",
)
def search_customers(
    q: str = Query(
        ...,
        min_length=2,
        max_length=100,
        description="Search term (minimum 2 non-whitespace characters, maximum 100 characters)",
    ),
    service: CustomerService = Depends(get_customer_service),
) -> List[CustomerResponse]:
    trimmed_query = q.strip()
    if len(trimmed_query) < 2:
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": ["query", "q"],
                    "msg": "Search query must contain at least 2 non-whitespace characters.",
                    "type": "value_error.min_length",
                }
            ],
        )
    return service.search_customers(trimmed_query)


@router.post(
    "",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new customer",
    description="Registers a new customer record with a unique identifier and timestamp.",
)
def create_customer(
    customer_in: CustomerCreate,
    service: CustomerService = Depends(get_customer_service),
) -> CustomerResponse:
    try:
        return service.create_customer(customer_in)
    except CustomerAlreadyExistsError as err:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(err),
        ) from err


@router.get(
    "",
    response_model=List[CustomerResponse],
    status_code=status.HTTP_200_OK,
    summary="List customers",
    description=(
        "Retrieves registered customers in storage order. Without `limit` and `offset`, "
        "returns the complete collection."
    ),
)
def get_all_customers(
    limit: Optional[int] = Query(
        None,
        ge=1,
        le=100,
        description="Maximum number of customers to return (1 to 100). When omitted, no upper bound is applied.",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="Number of customers to skip from the start of the collection.",
    ),
    service: CustomerService = Depends(get_customer_service),
) -> List[CustomerResponse]:
    return service.get_all_customers(limit=limit, offset=offset)
