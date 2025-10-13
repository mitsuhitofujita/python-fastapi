"""State domain validators."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.exceptions import DuplicateCodeError, EntityNotFoundError
from models.country import Country
from models.state import State


async def validate_country_exists(db: AsyncSession, country_id: int) -> None:
    """
    Validate that a country exists.

    Args:
        db: Database session
        country_id: Country ID to validate

    Raises:
        EntityNotFoundError: If the country does not exist
    """
    stmt = select(Country).where(Country.id == country_id)
    result = await db.execute(stmt)
    country = result.scalar_one_or_none()

    if country is None:
        raise EntityNotFoundError(entity_type="Country", entity_id=country_id)


async def validate_state_code_unique(
    db: AsyncSession, code: str, exclude_id: int | None = None
) -> None:
    """
    Validate that a state code is unique.

    Args:
        db: Database session
        code: State code to validate
        exclude_id: Optional state ID to exclude from check (for updates)

    Raises:
        DuplicateCodeError: If the code already exists
    """
    stmt = select(State).where(State.code == code)
    if exclude_id is not None:
        stmt = stmt.where(State.id != exclude_id)

    result = await db.execute(stmt)
    existing_state = result.scalar_one_or_none()

    if existing_state is not None:
        raise DuplicateCodeError(entity_type="State", code=code)
