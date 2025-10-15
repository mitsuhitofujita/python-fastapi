"""State API router."""

import json

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud.country import RequestInfo
from crud.state import create_state, delete_state, get_state, get_states, update_state
from database import get_db
from schemas.state import (
    StateCreateRequest,
    StateCreateResponse,
    StateResponse,
    StateUpdateRequest,
    StateUpdateResponse,
)

from .utils import get_client_ip

router = APIRouter(prefix="/states", tags=["states"])


@router.post(
    "/",
    response_model=StateCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a state/province",
    description="Create a new state/province and record event log",
)
async def create_state_endpoint(
    state: StateCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),  # noqa: B008 - FastAPI dependency injection pattern
):
    """
    Create a state/province

    - **country_id**: Country ID
    - **name**: State/province name (1-100 characters)
    - **code**: ISO 3166-2 code (automatically converted to uppercase)
    """
    request_info = RequestInfo(
        method=request.method,
        path=str(request.url.path),
        body=json.dumps(state.model_dump()),
        ip_address=get_client_ip(request),
        status_code=201,
    )

    created_state = await create_state(db, state, request_info)
    return created_state


@router.get(
    "/{state_id}",
    response_model=StateResponse,
    summary="Get a state/province",
    description="Get a state/province by ID",
)
async def read_state(
    state_id: int,
    db: AsyncSession = Depends(get_db),  # noqa: B008 - FastAPI dependency injection pattern
):
    """
    Get a state/province by ID

    - **state_id**: State/province ID
    """
    state = await get_state(db, state_id)
    return state


@router.get(
    "/",
    response_model=list[StateResponse],
    summary="Get list of states/provinces",
    description="Get list of states/provinces (with pagination support)",
)
async def read_states(
    skip: int = 0,
    limit: int = 100,
    country_id: int | None = None,
    db: AsyncSession = Depends(get_db),  # noqa: B008 - FastAPI dependency injection pattern
):
    """
    Get list of states/provinces

    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to retrieve (default: 100)
    - **country_id**: Filter by country ID (optional)
    """
    states = await get_states(db, skip=skip, limit=limit, country_id=country_id)
    return states


@router.put(
    "/{state_id}",
    response_model=StateUpdateResponse,
    summary="Update a state/province",
    description="Update a state/province by ID and record event log",
)
async def update_state_endpoint(
    state_id: int,
    state: StateUpdateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),  # noqa: B008 - FastAPI dependency injection pattern
):
    """
    Update a state/province

    - **state_id**: State/province ID
    - **country_id**: Country ID (optional)
    - **name**: State/province name (optional)
    - **code**: ISO 3166-2 code (optional, automatically converted to uppercase)
    """
    request_info = RequestInfo(
        method=request.method,
        path=str(request.url.path),
        body=json.dumps(state.model_dump(exclude_unset=True)),
        ip_address=get_client_ip(request),
        status_code=200,
    )

    updated_state = await update_state(db, state_id, state, request_info)
    return updated_state


@router.delete(
    "/{state_id}",
    response_model=StateResponse,
    summary="Delete a state/province",
    description="Delete a state/province by ID and record event log",
)
async def delete_state_endpoint(
    state_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),  # noqa: B008 - FastAPI dependency injection pattern
):
    """
    Delete a state/province

    - **state_id**: State/province ID
    """
    request_info = RequestInfo(
        method=request.method,
        path=str(request.url.path),
        ip_address=get_client_ip(request),
        status_code=200,
    )

    deleted_state = await delete_state(db, state_id, request_info)
    return deleted_state
