"""State CRUD operations."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from crud.country import RequestInfo
from domain.validators import (
    validate_country_exists,
    validate_state_code_unique,
)
from models.event_log import EventLog
from models.state import State
from schemas.state import StateCreateRequest, StateUpdateRequest


async def create_state(
    db: AsyncSession, state_data: StateCreateRequest, request_info: RequestInfo
) -> State:
    """
    Create a state/province and record event log (Transactional Outbox pattern)

    Args:
        db: Database session
        state_data: State creation data
        request_info: Request information

    Returns:
        Created state

    Raises:
        EntityNotFoundError: If country doesn't exist
        DuplicateCodeError: If code already exists
        IntegrityError: If an unexpected database error occurs
    """
    # Domain validation: check country exists and code is unique
    await validate_country_exists(db, state_data.country_id)
    await validate_state_code_unique(db, state_data.code)

    try:
        # 1. Create business data
        state = State(
            country_id=state_data.country_id,
            name=state_data.name,
            code=state_data.code,
        )
        db.add(state)
        await db.flush()  # Commit ID

        # 2. Record event log
        event_log = EventLog(
            event_type="CREATE",
            entity_type="state",
            entity_id=state.id,
            request_method=request_info.method,
            request_path=request_info.path,
            request_body=request_info.body,
            user_id=request_info.user_id,
            ip_address=request_info.ip_address,
            status_code=request_info.status_code,
            processing_status="completed",
        )
        db.add(event_log)
        await db.commit()  # Commit both together

        await db.refresh(state)
        return state
    except IntegrityError:
        await db.rollback()
        # Re-raise as unexpected error (validation should have caught issues)
        raise


async def get_state(db: AsyncSession, state_id: int) -> State:
    """
    Get a state/province

    Args:
        db: Database session
        state_id: State ID

    Returns:
        State

    Raises:
        EntityNotFoundError: If state not found
    """
    result = await db.execute(select(State).where(State.id == state_id))
    state = result.scalar_one_or_none()
    if state is None:
        from domain.exceptions import EntityNotFoundError

        raise EntityNotFoundError("State", state_id)
    return state


async def get_states(
    db: AsyncSession, skip: int = 0, limit: int = 100, country_id: int | None = None
) -> list[State]:
    """
    Get list of states/provinces (with pagination support)

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to retrieve
        country_id: Filter by country ID (optional)

    Returns:
        List of states
    """
    query = select(State)
    if country_id is not None:
        query = query.where(State.country_id == country_id)
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def update_state(
    db: AsyncSession,
    state_id: int,
    state_data: StateUpdateRequest,
    request_info: RequestInfo,
) -> State:
    """
    Update a state/province and record event log (Transactional Outbox pattern)

    Args:
        db: Database session
        state_id: State ID
        state_data: State update data
        request_info: Request information

    Returns:
        Updated state

    Raises:
        EntityNotFoundError: If state or country doesn't exist
        DuplicateCodeError: If code already exists
        IntegrityError: If an unexpected database error occurs
    """
    # Get target state
    result = await db.execute(select(State).where(State.id == state_id))
    state = result.scalar_one_or_none()

    if state is None:
        from domain.exceptions import EntityNotFoundError

        raise EntityNotFoundError("State", state_id)

    # Domain validation: check country exists if being changed
    if state_data.country_id is not None and state_data.country_id != state.country_id:
        await validate_country_exists(db, state_data.country_id)

    # Domain validation: check code uniqueness if being changed
    if state_data.code is not None and state_data.code != state.code:
        await validate_state_code_unique(db, state_data.code, exclude_id=state_id)

    try:
        # 1. Update business data
        if state_data.country_id is not None:
            state.country_id = state_data.country_id  # type: ignore[assignment]
        if state_data.name is not None:
            state.name = state_data.name  # type: ignore[assignment]
        if state_data.code is not None:
            state.code = state_data.code  # type: ignore[assignment]

        await db.flush()  # Commit changes

        # 2. Record event log
        event_log = EventLog(
            event_type="UPDATE",
            entity_type="state",
            entity_id=state.id,
            request_method=request_info.method,
            request_path=request_info.path,
            request_body=request_info.body,
            user_id=request_info.user_id,
            ip_address=request_info.ip_address,
            status_code=request_info.status_code,
            processing_status="completed",
        )
        db.add(event_log)
        await db.commit()  # Commit both together

        await db.refresh(state)
        return state
    except IntegrityError:
        await db.rollback()
        # Re-raise as unexpected error (validation should have caught issues)
        raise


async def delete_state(
    db: AsyncSession, state_id: int, request_info: RequestInfo
) -> State:
    """
    Delete a state/province and record event log (Transactional Outbox pattern)

    Args:
        db: Database session
        state_id: State ID
        request_info: Request information

    Returns:
        Deleted state

    Raises:
        EntityNotFoundError: If state not found
    """
    # Get target state
    result = await db.execute(select(State).where(State.id == state_id))
    state = result.scalar_one_or_none()

    if state is None:
        from domain.exceptions import EntityNotFoundError

        raise EntityNotFoundError("State", state_id)

    # 1. Record event log (before deletion to capture ID)
    event_log = EventLog(
        event_type="DELETE",
        entity_type="state",
        entity_id=state.id,
        request_method=request_info.method,
        request_path=request_info.path,
        request_body=request_info.body,
        user_id=request_info.user_id,
        ip_address=request_info.ip_address,
        status_code=request_info.status_code,
        processing_status="completed",
    )
    db.add(event_log)

    # 2. Delete business data
    await db.delete(state)
    await db.commit()  # Commit both together

    return state
