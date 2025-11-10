"""City CRUD operations."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from crud.country import RequestInfo
from domain.validators import validate_state_exists
from domain.validators.city import validate_city_code_unique
from models.city import City
from models.event_log import EventLog
from schemas.city import CityCreateRequest, CityUpdateRequest


async def create_city(
    db: AsyncSession, city_data: CityCreateRequest, request_info: RequestInfo
) -> City:
    """
    Create a city and record event log (Transactional Outbox pattern)

    Args:
        db: Database session
        city_data: City creation data
        request_info: Request information

    Returns:
        Created city

    Raises:
        EntityNotFoundError: If state doesn't exist
        DuplicateCodeError: If active city code already exists
        IntegrityError: If an unexpected database error occurs
    """
    # Domain validation: check state exists and code is unique
    await validate_state_exists(db, city_data.state_id)
    await validate_city_code_unique(db, city_data.code)

    try:
        # 1. Create business data
        city = City(
            state_id=city_data.state_id,
            name=city_data.name,
            code=city_data.code,
            is_active=city_data.is_active,
        )
        db.add(city)
        await db.flush()  # Commit ID

        # 2. Record event log
        event_log = EventLog(
            event_type="CREATE",
            entity_type="city",
            entity_id=city.id,
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

        await db.refresh(city)
        return city
    except IntegrityError:
        await db.rollback()
        # Re-raise as unexpected error (validation should have caught issues)
        raise


async def get_city(
    db: AsyncSession, city_id: int, include_inactive: bool = False
) -> City:
    """
    Get a city

    Args:
        db: Database session
        city_id: City ID
        include_inactive: If True, include inactive cities

    Returns:
        City

    Raises:
        EntityNotFoundError: If city not found
    """
    query = select(City).where(City.id == city_id)
    if not include_inactive:
        query = query.where(City.is_active == True)  # noqa: E712

    result = await db.execute(query)
    city = result.scalar_one_or_none()
    if city is None:
        from domain.exceptions import EntityNotFoundError

        raise EntityNotFoundError("City", city_id)
    return city


async def list_cities(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
) -> list[City]:
    """
    Get list of cities (with pagination support)

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to retrieve
        include_inactive: If True, include inactive cities

    Returns:
        List of cities
    """
    query = select(City)
    if not include_inactive:
        query = query.where(City.is_active == True)  # noqa: E712
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def list_cities_by_state(
    db: AsyncSession,
    state_id: int,
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
) -> list[City]:
    """
    Get list of cities filtered by state (with pagination support)

    Args:
        db: Database session
        state_id: State ID to filter by
        skip: Number of records to skip
        limit: Maximum number of records to retrieve
        include_inactive: If True, include inactive cities

    Returns:
        List of cities for the specified state
    """
    query = select(City).where(City.state_id == state_id)
    if not include_inactive:
        query = query.where(City.is_active == True)  # noqa: E712
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def update_city(
    db: AsyncSession,
    city_id: int,
    city_data: CityUpdateRequest,
    request_info: RequestInfo,
    include_inactive: bool = False,
) -> City:
    """
    Update a city and record event log (Transactional Outbox pattern)

    Args:
        db: Database session
        city_id: City ID
        city_data: City update data
        request_info: Request information
        include_inactive: If True, allow updating inactive cities

    Returns:
        Updated city

    Raises:
        EntityNotFoundError: If city doesn't exist
        DuplicateCodeError: If active city code already exists
        IntegrityError: If an unexpected database error occurs
    """
    # Get target city
    query = select(City).where(City.id == city_id)
    if not include_inactive:
        query = query.where(City.is_active == True)  # noqa: E712

    result = await db.execute(query)
    city = result.scalar_one_or_none()

    if city is None:
        from domain.exceptions import EntityNotFoundError

        raise EntityNotFoundError("City", city_id)

    # Domain validation: check code uniqueness if being changed
    if city_data.code is not None and city_data.code != city.code:
        await validate_city_code_unique(db, city_data.code, exclude_id=city_id)

    try:
        # 1. Update business data
        if city_data.name is not None:
            city.name = city_data.name  # type: ignore[assignment]
        if city_data.code is not None:
            city.code = city_data.code  # type: ignore[assignment]
        if city_data.is_active is not None:
            city.is_active = city_data.is_active  # type: ignore[assignment]

        await db.flush()  # Commit changes

        # 2. Record event log
        event_log = EventLog(
            event_type="UPDATE",
            entity_type="city",
            entity_id=city.id,
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

        await db.refresh(city)
        return city
    except IntegrityError:
        await db.rollback()
        # Re-raise as unexpected error (validation should have caught issues)
        raise


async def delete_city(
    db: AsyncSession,
    city_id: int,
    request_info: RequestInfo,
    include_inactive: bool = False,
) -> City:
    """
    Delete a city and record event log (Transactional Outbox pattern)

    Args:
        db: Database session
        city_id: City ID
        request_info: Request information
        include_inactive: If True, allow deleting inactive cities

    Returns:
        Deleted city

    Raises:
        EntityNotFoundError: If city not found
        RelatedEntityExistsError: If city has related entities (future)
    """
    # Get target city
    query = select(City).where(City.id == city_id)
    if not include_inactive:
        query = query.where(City.is_active == True)  # noqa: E712

    result = await db.execute(query)
    city = result.scalar_one_or_none()

    if city is None:
        from domain.exceptions import EntityNotFoundError

        raise EntityNotFoundError("City", city_id)

    # TODO: Future expansion - check for related entities (e.g., Address)
    # When implementing related entities, add validation here similar to:
    # from models.address import Address
    # addresses_result = await db.execute(
    #     select(Address).where(Address.city_id == city_id).limit(1)
    # )
    # if addresses_result.scalar_one_or_none() is not None:
    #     from domain.exceptions import RelatedEntityExistsError
    #     raise RelatedEntityExistsError("City", city_id, "addresses")

    # 1. Record event log (before deletion to capture ID)
    event_log = EventLog(
        event_type="DELETE",
        entity_type="city",
        entity_id=city.id,
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
    await db.delete(city)
    await db.commit()  # Commit both together

    return city
