"""Country domain validators."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.exceptions import DuplicateCodeError
from models.country import Country


async def validate_country_code_unique(
    db: AsyncSession, code: str, exclude_id: int | None = None
) -> None:
    """
    Validate that a country code is unique.

    Args:
        db: Database session
        code: Country code to validate
        exclude_id: Optional country ID to exclude from check (for updates)

    Raises:
        DuplicateCodeError: If the code already exists
    """
    stmt = select(Country).where(Country.code == code)
    if exclude_id is not None:
        stmt = stmt.where(Country.id != exclude_id)

    result = await db.execute(stmt)
    existing_country = result.scalar_one_or_none()

    if existing_country is not None:
        raise DuplicateCodeError(entity_type="Country", code=code)
