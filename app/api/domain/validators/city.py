"""City domain validators."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.exceptions import DuplicateCodeError, EntityNotFoundError
from models.city import City
from models.state import State


async def validate_state_exists(db: AsyncSession, state_id: int) -> None:
    """
    Validate that a state exists.

    Args:
        db: Database session
        state_id: State ID to validate

    Raises:
        EntityNotFoundError: If the state does not exist
    """
    stmt = select(State).where(State.id == state_id)
    result = await db.execute(stmt)
    state = result.scalar_one_or_none()

    if state is None:
        raise EntityNotFoundError(entity_type="State", entity_id=state_id)


async def validate_city_code_unique(
    db: AsyncSession, code: str, exclude_id: int | None = None
) -> None:
    """
    Validate that the active city code is unique.

    Only cities with is_active=True are checked for uniqueness.
    This allows the same code to be reused for inactive cities
    (e.g., municipalities that were merged or abolished).

    Args:
        db: Database session
        code: City code to validate
        exclude_id: City ID to exclude from the check (for updates)

    Raises:
        DuplicateCodeError: If an active city with the same code already exists
    """
    # Only check uniqueness for active cities (is_active=True)
    # Using == True instead of 'is True' for SQLAlchemy query
    stmt = select(City).where(City.code == code, City.is_active == True)  # noqa: E712
    if exclude_id is not None:
        stmt = stmt.where(City.id != exclude_id)

    result = await db.execute(stmt)
    existing_city = result.scalar_one_or_none()

    if existing_city is not None:
        raise DuplicateCodeError(entity_type="Active city", code=code)
