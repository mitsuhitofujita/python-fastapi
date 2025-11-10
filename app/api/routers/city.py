"""City API router."""

import json

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud.city import (
    RequestInfo,
    create_city,
    delete_city,
    get_city,
    list_cities,
    update_city,
)
from database import get_db
from schemas.city import (
    CityCreateRequest,
    CityCreateResponse,
    CityResponse,
    CityUpdateRequest,
    CityUpdateResponse,
)

from .utils import get_client_ip

router = APIRouter(prefix="/cities", tags=["cities"])


@router.post(
    "/",
    response_model=CityCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a city",
    description="Create a new city and record event log",
)
async def create_city_endpoint(
    city: CityCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),  # noqa: B008 - FastAPI dependency injection pattern
):
    """
    Create a city

    - **state_id**: State ID that this city belongs to
    - **name**: City name (1-100 characters)
    - **code**: 6-digit city code (JIS X 0402 standard)
    - **is_active**: Whether the city is currently active (default: True)
    """
    request_info = RequestInfo(
        method=request.method,
        path=str(request.url.path),
        body=json.dumps(city.model_dump()),
        ip_address=get_client_ip(request),
        status_code=201,
    )

    created_city = await create_city(db, city, request_info)
    return created_city


@router.get(
    "/{city_id}",
    response_model=CityResponse,
    summary="Get a city",
    description="Get a city by ID",
)
async def read_city(
    city_id: int,
    include_inactive: bool = Query(
        default=False, description="Include inactive cities in search"
    ),
    db: AsyncSession = Depends(get_db),  # noqa: B008 - FastAPI dependency injection pattern
):
    """
    Get a city by ID

    - **city_id**: City ID
    - **include_inactive**: Include inactive cities (default: False)
    """
    city = await get_city(db, city_id, include_inactive=include_inactive)
    return city


@router.get(
    "/",
    response_model=list[CityResponse],
    summary="Get list of cities",
    description="Get list of cities (with pagination and active status filtering)",
)
async def read_cities(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(
        default=100, ge=1, le=1000, description="Maximum number of records to retrieve"
    ),
    include_inactive: bool = Query(
        default=False, description="Include inactive cities in results"
    ),
    db: AsyncSession = Depends(get_db),  # noqa: B008 - FastAPI dependency injection pattern
):
    """
    Get list of cities

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to retrieve (default: 100, max: 1000)
    - **include_inactive**: Include inactive cities (default: False)
    """
    cities = await list_cities(
        db, skip=skip, limit=limit, include_inactive=include_inactive
    )
    return cities


@router.put(
    "/{city_id}",
    response_model=CityUpdateResponse,
    summary="Update a city",
    description="Update a city by ID and record event log",
)
async def update_city_endpoint(
    city_id: int,
    city: CityUpdateRequest,
    request: Request,
    include_inactive: bool = Query(
        default=False, description="Include inactive cities in search"
    ),
    db: AsyncSession = Depends(get_db),  # noqa: B008 - FastAPI dependency injection pattern
):
    """
    Update a city

    - **city_id**: City ID
    - **name**: City name (optional)
    - **code**: 6-digit city code (optional)
    - **is_active**: Active status (optional)
    - **include_inactive**: Include inactive cities in search (default: False)
    """
    request_info = RequestInfo(
        method=request.method,
        path=str(request.url.path),
        body=json.dumps(city.model_dump(exclude_unset=True)),
        ip_address=get_client_ip(request),
        status_code=200,
    )

    updated_city = await update_city(
        db, city_id, city, request_info, include_inactive=include_inactive
    )
    return updated_city


@router.delete(
    "/{city_id}",
    response_model=CityResponse,
    summary="Delete a city",
    description="Delete a city by ID and record event log",
)
async def delete_city_endpoint(
    city_id: int,
    request: Request,
    include_inactive: bool = Query(
        default=False, description="Include inactive cities in search"
    ),
    db: AsyncSession = Depends(get_db),  # noqa: B008 - FastAPI dependency injection pattern
):
    """
    Delete a city

    - **city_id**: City ID
    - **include_inactive**: Include inactive cities in search (default: False)
    """
    request_info = RequestInfo(
        method=request.method,
        path=str(request.url.path),
        ip_address=get_client_ip(request),
        status_code=200,
    )

    deleted_city = await delete_city(
        db, city_id, request_info, include_inactive=include_inactive
    )
    return deleted_city
