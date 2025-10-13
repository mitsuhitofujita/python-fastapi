"""Country CRUD operations."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from domain.validators import validate_country_code_unique
from models.country import Country
from models.event_log import EventLog
from schemas.country import CountryCreateRequest, CountryUpdateRequest


class RequestInfo:
    """Data class to hold request information"""

    def __init__(
        self,
        method: str,
        path: str,
        body: str | None = None,
        ip_address: str | None = None,
        user_id: str | None = None,
        status_code: int | None = None,
    ):
        self.method = method
        self.path = path
        self.body = body
        self.ip_address = ip_address
        self.user_id = user_id
        self.status_code = status_code


async def create_country(
    db: AsyncSession, country_data: CountryCreateRequest, request_info: RequestInfo
) -> Country:
    """
    Create a country and record an event log (Transactional Outbox pattern)

    Args:
        db: Database session
        country_data: Country creation data
        request_info: Request information

    Returns:
        Created country

    Raises:
        DuplicateCodeError: If country code already exists
        IntegrityError: If an unexpected database error occurs
    """
    # Domain validation: check code uniqueness
    await validate_country_code_unique(db, country_data.code)

    try:
        # 1. Create business data
        country = Country(name=country_data.name, code=country_data.code)
        db.add(country)
        await db.flush()  # Confirm ID

        # 2. Record event log
        event_log = EventLog(
            event_type="CREATE",
            entity_type="country",
            entity_id=country.id,
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

        await db.refresh(country)
        return country
    except IntegrityError:
        await db.rollback()
        # Re-raise as unexpected error (validation should have caught duplicates)
        raise


async def get_country(db: AsyncSession, country_id: int) -> Country | None:
    """
    Get a country

    Args:
        db: Database session
        country_id: Country ID

    Returns:
        Country (None if not found)
    """
    result = await db.execute(select(Country).where(Country.id == country_id))
    return result.scalar_one_or_none()


async def get_countries(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> list[Country]:
    """
    Get list of countries (with pagination)

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to retrieve

    Returns:
        List of countries
    """
    result = await db.execute(select(Country).offset(skip).limit(limit))
    return list(result.scalars().all())


async def update_country(
    db: AsyncSession,
    country_id: int,
    country_data: CountryUpdateRequest,
    request_info: RequestInfo,
) -> Country | None:
    """
    Update a country and record an event log (Transactional Outbox pattern)

    Args:
        db: Database session
        country_id: Country ID
        country_data: Country update data
        request_info: Request information

    Returns:
        Updated country (None if not found)

    Raises:
        DuplicateCodeError: If country code already exists
        IntegrityError: If an unexpected database error occurs
    """
    # Get target country
    result = await db.execute(select(Country).where(Country.id == country_id))
    country = result.scalar_one_or_none()

    if country is None:
        return None

    # Domain validation: check code uniqueness if code is being changed
    if country_data.code is not None and country_data.code != country.code:
        await validate_country_code_unique(db, country_data.code, exclude_id=country_id)

    try:
        # 1. Update business data
        if country_data.name is not None:
            country.name = country_data.name  # type: ignore[assignment]
        if country_data.code is not None:
            country.code = country_data.code  # type: ignore[assignment]

        await db.flush()  # Confirm changes

        # 2. Record event log
        event_log = EventLog(
            event_type="UPDATE",
            entity_type="country",
            entity_id=country.id,
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

        await db.refresh(country)
        return country
    except IntegrityError:
        await db.rollback()
        # Re-raise as unexpected error (validation should have caught duplicates)
        raise


async def delete_country(
    db: AsyncSession, country_id: int, request_info: RequestInfo
) -> Country | None:
    """
    Delete a country and record an event log (Transactional Outbox pattern)

    Args:
        db: Database session
        country_id: Country ID
        request_info: Request information

    Returns:
        Deleted country (None if not found)
    """
    # Get target country
    result = await db.execute(select(Country).where(Country.id == country_id))
    country = result.scalar_one_or_none()

    if country is None:
        return None

    # 1. Record event log (before deletion to record ID)
    event_log = EventLog(
        event_type="DELETE",
        entity_type="country",
        entity_id=country.id,
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
    await db.delete(country)
    await db.commit()  # Commit both together

    return country
