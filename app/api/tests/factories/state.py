"""Factory Boy factories for State model."""

import factory
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from models.state import State
from tests.factories.country import create_country_async

fake = Faker()


class StateFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating State instances for tests."""

    class Meta:
        model = State
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n)
    country_id = factory.Sequence(lambda n: n)
    name = factory.LazyAttribute(lambda _: fake.city())
    code = factory.LazyAttribute(lambda _: f"{fake.country_code()}-{fake.random_int(1, 99):02d}")


async def create_state_async(
    db: AsyncSession,
    **kwargs,
) -> State:
    """Create a State instance asynchronously.

    Args:
        db: Database session
        **kwargs: State attributes to override

    Returns:
        Created State instance
    """
    # If country_id not provided, create a new country
    country_id = kwargs.get("country_id")
    if country_id is None:
        country = await create_country_async(db)
        country_id = country.id

    state = State(
        country_id=country_id,
        name=kwargs.get("name", fake.city()),
        code=kwargs.get("code", f"{fake.country_code()}-{fake.random_int(1, 99):02d}"),
    )
    db.add(state)
    await db.commit()
    await db.refresh(state)
    return state
