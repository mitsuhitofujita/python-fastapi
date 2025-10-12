import json

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from crud.country import RequestInfo
from crud.state import delete_state, get_state, get_states, update_state
from database import get_db
from schemas.state import StateResponse, StateUpdate

router = APIRouter(prefix="/states", tags=["states"])


def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    # Check X-Forwarded-For header (when behind proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    # Direct connection
    return request.client.host if request.client else "unknown"


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
    if state is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"State with id {state_id} not found",
        )
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
    response_model=StateResponse,
    summary="Update a state/province",
    description="Update a state/province by ID and record event log",
)
async def update_state_endpoint(
    state_id: int,
    state: StateUpdate,
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

    try:
        updated_state = await update_state(db, state_id, state, request_info)
        if updated_state is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"State with id {state_id} not found",
            )
        return updated_state
    except IntegrityError as e:
        error_msg = str(e.orig) if hasattr(e, "orig") else str(e)
        if "foreign key" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Country with id {state.country_id} does not exist",
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"State with code '{state.code}' already exists",
        ) from e


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
    if deleted_state is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"State with id {state_id} not found",
        )
    return deleted_state
