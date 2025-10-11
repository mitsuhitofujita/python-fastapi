"""Unit tests for Country CRUD operations."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from crud.country import (
    RequestInfo,
    create_country,
    delete_country,
    get_countries,
    get_country,
    update_country,
)
from models.country import Country
from models.event_log import EventLog
from schemas.country import CountryCreate, CountryUpdate


@pytest.mark.asyncio
class TestCountryCRUD:
    """Test cases for Country CRUD operations."""

    async def test_create_country(self, db_session: AsyncSession):
        """Test creating a country records event log."""
        # Arrange
        country_data = CountryCreate(name="Japan", code="JP")
        request_info = RequestInfo(
            method="POST",
            path="/countries",
            body='{"name": "Japan", "code": "JP"}',
            ip_address="127.0.0.1",
            status_code=200,
        )

        # Act
        country = await create_country(db_session, country_data, request_info)

        # Assert - Country created
        assert country.id is not None
        assert country.name == "Japan"
        assert country.code == "JP"

        # Assert - Event log created
        result = await db_session.execute(select(EventLog))
        event_logs = result.scalars().all()
        assert len(event_logs) == 1
        assert event_logs[0].event_type == "CREATE"
        assert event_logs[0].entity_type == "country"
        assert event_logs[0].entity_id == country.id
        assert event_logs[0].request_method == "POST"
        assert event_logs[0].processing_status == "completed"

    async def test_get_country(self, db_session: AsyncSession):
        """Test retrieving a country by ID."""
        # Arrange
        country = Country(name="Japan", code="JP")
        db_session.add(country)
        await db_session.commit()
        await db_session.refresh(country)

        # Act
        result = await get_country(db_session, country.id)

        # Assert
        assert result is not None
        assert result.id == country.id
        assert result.name == "Japan"
        assert result.code == "JP"

    async def test_get_country_not_found(self, db_session: AsyncSession):
        """Test retrieving a non-existent country."""
        # Act
        result = await get_country(db_session, 999)

        # Assert
        assert result is None

    async def test_get_countries(self, db_session: AsyncSession):
        """Test retrieving all countries."""
        # Arrange
        countries_data = [
            Country(name="Japan", code="JP"),
            Country(name="United States", code="US"),
            Country(name="United Kingdom", code="GB"),
        ]
        for country in countries_data:
            db_session.add(country)
        await db_session.commit()

        # Act
        result = await get_countries(db_session)

        # Assert
        assert len(result) == 3
        assert all(isinstance(c, Country) for c in result)

    async def test_get_countries_pagination(self, db_session: AsyncSession):
        """Test retrieving countries with pagination."""
        # Arrange
        countries_data = [
            Country(name="Japan", code="JP"),
            Country(name="United States", code="US"),
            Country(name="United Kingdom", code="GB"),
        ]
        for country in countries_data:
            db_session.add(country)
        await db_session.commit()

        # Act
        result = await get_countries(db_session, skip=1, limit=1)

        # Assert
        assert len(result) == 1

    async def test_update_country(self, db_session: AsyncSession):
        """Test updating a country records event log."""
        # Arrange
        country = Country(name="Nippon", code="JP")
        db_session.add(country)
        await db_session.commit()
        await db_session.refresh(country)

        country_data = CountryUpdate(name="Japan")
        request_info = RequestInfo(
            method="PUT",
            path=f"/countries/{country.id}",
            body='{"name": "Japan"}',
            ip_address="127.0.0.1",
            status_code=200,
        )

        # Act
        result = await update_country(
            db_session, country.id, country_data, request_info
        )

        # Assert - Country updated
        assert result is not None
        assert result.id == country.id
        assert result.name == "Japan"
        assert result.code == "JP"

        # Assert - Event log created
        event_result = await db_session.execute(select(EventLog))
        event_logs = event_result.scalars().all()
        assert len(event_logs) == 1
        assert event_logs[0].event_type == "UPDATE"
        assert event_logs[0].entity_id == country.id

    async def test_update_country_not_found(self, db_session: AsyncSession):
        """Test updating a non-existent country."""
        # Arrange
        country_data = CountryUpdate(name="Japan")
        request_info = RequestInfo(
            method="PUT",
            path="/countries/999",
            ip_address="127.0.0.1",
            status_code=404,
        )

        # Act
        result = await update_country(db_session, 999, country_data, request_info)

        # Assert
        assert result is None

    async def test_delete_country(self, db_session: AsyncSession):
        """Test deleting a country records event log."""
        # Arrange
        country = Country(name="Japan", code="JP")
        db_session.add(country)
        await db_session.commit()
        await db_session.refresh(country)
        country_id = country.id

        request_info = RequestInfo(
            method="DELETE",
            path=f"/countries/{country_id}",
            ip_address="127.0.0.1",
            status_code=200,
        )

        # Act
        result = await delete_country(db_session, country_id, request_info)

        # Assert - Country deleted
        assert result is not None
        assert result.id == country_id

        # Verify country no longer exists
        country_result = await db_session.execute(select(Country))
        countries = country_result.scalars().all()
        assert len(countries) == 0

        # Assert - Event log created
        event_result = await db_session.execute(select(EventLog))
        event_logs = event_result.scalars().all()
        assert len(event_logs) == 1
        assert event_logs[0].event_type == "DELETE"
        assert event_logs[0].entity_id == country_id

    async def test_delete_country_not_found(self, db_session: AsyncSession):
        """Test deleting a non-existent country."""
        # Arrange
        request_info = RequestInfo(
            method="DELETE",
            path="/countries/999",
            ip_address="127.0.0.1",
            status_code=404,
        )

        # Act
        result = await delete_country(db_session, 999, request_info)

        # Assert
        assert result is None
