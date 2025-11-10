"""Factory Boy factories for City model."""

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from models.city import City
from tests.factories.state import create_state_async

fake = Faker("ja_JP")  # Japanese locale for realistic city names


async def create_city_async(
    db: AsyncSession,
    state_id: int | None = None,
    name: str | None = None,
    code: str | None = None,
    is_active: bool = True,
) -> City:
    """Create a City instance asynchronously.

    Args:
        db: Database session
        state_id: State ID (auto-created if not provided)
        name: City name (randomly generated if not provided)
        code: City code (randomly generated 6-digit number if not provided)
        is_active: Whether the city is active (default: True)

    Returns:
        Created City instance
    """
    # Auto-create state if not provided
    if state_id is None:
        state = await create_state_async(db)
        state_id = state.id

    # Generate random name if not provided
    if name is None:
        name = fake.city()  # Japanese city name

    # Generate random 6-digit code if not provided
    if code is None:
        code = fake.numerify(text="######")  # 6-digit random number

    city = City(
        state_id=state_id,
        name=name,
        code=code,
        is_active=is_active,
    )
    db.add(city)
    await db.commit()
    await db.refresh(city)
    return city
