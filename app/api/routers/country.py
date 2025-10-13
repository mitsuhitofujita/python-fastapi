"""Country API router."""

import json

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from crud.country import (
    RequestInfo,
    create_country,
    delete_country,
    get_countries,
    get_country,
    update_country,
)
from crud.state import get_states
from database import get_db
from domain.exceptions import DuplicateCodeError
from schemas.country import (
    CountryCreateRequest,
    CountryCreateResponse,
    CountryResponse,
    CountryUpdateRequest,
    CountryUpdateResponse,
)
from schemas.state import StateResponse

from .utils import get_client_ip

router = APIRouter(prefix="/countries", tags=["countries"])


@router.post(
    "/",
    response_model=CountryCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a country",
    description="Create a new country and record event log",
)
async def create_country_endpoint(
    country: CountryCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),  # noqa: B008 - FastAPI dependency injection pattern
):
    """
    Create a country

    - **name**: Country name (1-100 characters)
    - **code**: ISO 3166-1 alpha-2 country code (2 characters, automatically converted to uppercase)
    """
    request_info = RequestInfo(
        method=request.method,
        path=str(request.url.path),
        body=json.dumps(country.model_dump()),
        ip_address=get_client_ip(request),
        status_code=201,
    )

    try:
        created_country = await create_country(db, country, request_info)
        return created_country
    except DuplicateCodeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        ) from e
    except IntegrityError as e:
        # Unexpected database error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        ) from e


@router.get(
    "/{country_id}",
    response_model=CountryResponse,
    summary="Get a country",
    description="Get a country by its ID",
)
async def read_country(
    country_id: int,
    db: AsyncSession = Depends(get_db),  # noqa: B008 - FastAPI dependency injection pattern
):
    """
    Get a country by ID

    - **country_id**: Country ID
    """
    country = await get_country(db, country_id)
    if country is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country with id {country_id} not found",
        )
    return country


@router.get(
    "/",
    response_model=list[CountryResponse],
    summary="Get list of countries",
    description="Get list of countries (with pagination support)",
)
async def read_countries(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),  # noqa: B008 - FastAPI dependency injection pattern
):
    """
    Get list of countries

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to retrieve (default: 100)
    """
    countries = await get_countries(db, skip=skip, limit=limit)
    return countries


@router.put(
    "/{country_id}",
    response_model=CountryUpdateResponse,
    summary="Update a country",
    description="Update a country by its ID and record event log",
)
async def update_country_endpoint(
    country_id: int,
    country: CountryUpdateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),  # noqa: B008 - FastAPI dependency injection pattern
):
    """
    Update a country

    - **country_id**: Country ID
    - **name**: Country name (optional)
    - **code**: ISO 3166-1 alpha-2 country code (optional, automatically converted to uppercase)
    """
    request_info = RequestInfo(
        method=request.method,
        path=str(request.url.path),
        body=json.dumps(country.model_dump(exclude_unset=True)),
        ip_address=get_client_ip(request),
        status_code=200,
    )

    try:
        updated_country = await update_country(db, country_id, country, request_info)
        if updated_country is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Country with id {country_id} not found",
            )
        return updated_country
    except DuplicateCodeError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message,
        ) from e
    except IntegrityError as e:
        # Unexpected database error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        ) from e


@router.delete(
    "/{country_id}",
    response_model=CountryResponse,
    summary="Delete a country",
    description="Delete a country by its ID and record event log",
)
async def delete_country_endpoint(
    country_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),  # noqa: B008 - FastAPI dependency injection pattern
):
    """
    Delete a country

    - **country_id**: Country ID
    """
    request_info = RequestInfo(
        method=request.method,
        path=str(request.url.path),
        ip_address=get_client_ip(request),
        status_code=200,
    )

    try:
        deleted_country = await delete_country(db, country_id, request_info)
        if deleted_country is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Country with id {country_id} not found",
            )
        return deleted_country
    except IntegrityError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete country with existing states",
        ) from e


@router.get(
    "/{country_id}/states",
    response_model=list[StateResponse],
    summary="Get states/provinces of a country",
    description="Get list of states/provinces for a specific country",
)
async def read_country_states(
    country_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),  # noqa: B008 - FastAPI dependency injection pattern
):
    """
    Get list of states/provinces for a specific country

    - **country_id**: Country ID
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to retrieve (default: 100)
    """
    # Verify country exists
    country = await get_country(db, country_id)
    if country is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Country with id {country_id} not found",
        )

    states = await get_states(db, skip=skip, limit=limit, country_id=country_id)
    return states
