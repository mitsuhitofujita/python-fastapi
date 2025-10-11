"""Factory Boy factories for Country model."""

import factory
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from models.country import Country

fake = Faker()


class CountryFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for creating Country instances for tests."""

    class Meta:
        model = Country
        sqlalchemy_session_persistence = "commit"

    id = factory.Sequence(lambda n: n)
    name = factory.LazyAttribute(lambda _: fake.country())
    code = factory.LazyAttribute(lambda _: fake.country_code())


async def create_country_async(
    db: AsyncSession,
    **kwargs,
) -> Country:
    """Create a Country instance asynchronously.

    Args:
        db: Database session
        **kwargs: Country attributes to override

    Returns:
        Created Country instance
    """
    country = Country(
        name=kwargs.get("name", fake.country()),
        code=kwargs.get("code", fake.country_code()),
    )
    db.add(country)
    await db.commit()
    await db.refresh(country)
    return country
