"""Integration tests for Country API endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.country import Country
from models.event_log import EventLog
from tests.factories.country import create_country_async


@pytest.mark.asyncio
class TestCountryAPI:
    """Test cases for Country API endpoints."""

    async def test_create_country(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating a new country."""
        # Arrange
        payload = {"name": "Japan", "code": "JP"}

        # Act
        response = await client.post("/countries/", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Japan"
        assert data["code"] == "JP"
        assert "id" in data

        # Verify database state
        result = await db_session.execute(select(Country))
        countries = result.scalars().all()
        assert len(countries) == 1
        assert countries[0].name == "Japan"
        assert countries[0].code == "JP"

        # Verify event log
        event_result = await db_session.execute(select(EventLog))
        event_logs = event_result.scalars().all()
        assert len(event_logs) == 1
        assert event_logs[0].event_type == "CREATE"
        assert event_logs[0].entity_type == "country"
        assert event_logs[0].entity_id == data["id"]
        assert event_logs[0].request_method == "POST"
        assert event_logs[0].request_path == "/countries/"
        assert event_logs[0].ip_address is not None
        assert event_logs[0].processing_status == "completed"

    async def test_get_country(self, client: AsyncClient, db_session: AsyncSession):
        """Test retrieving a country by ID."""
        # Arrange
        country = await create_country_async(
            db_session, name="United States", code="US"
        )

        # Act
        response = await client.get(f"/countries/{country.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == country.id
        assert data["name"] == "United States"
        assert data["code"] == "US"

    async def test_get_country_not_found(self, client: AsyncClient):
        """Test retrieving a non-existent country."""
        # Act
        response = await client.get("/countries/999")

        # Assert
        assert response.status_code == 404

    async def test_list_countries(self, client: AsyncClient, db_session: AsyncSession):
        """Test listing countries with pagination."""
        # Arrange
        await create_country_async(db_session, name="Japan", code="JP")
        await create_country_async(db_session, name="United States", code="US")
        await create_country_async(db_session, name="United Kingdom", code="GB")

        # Act
        response = await client.get("/countries/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("id" in country for country in data)
        assert all("name" in country for country in data)
        assert all("code" in country for country in data)

    async def test_list_countries_pagination(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test listing countries with pagination parameters."""
        # Arrange
        await create_country_async(db_session, name="Japan", code="JP")
        await create_country_async(db_session, name="United States", code="US")
        await create_country_async(db_session, name="United Kingdom", code="GB")

        # Act
        response = await client.get("/countries/?skip=1&limit=1")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    async def test_update_country(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating a country."""
        # Arrange
        country = await create_country_async(db_session, name="Nippon", code="JP")

        # Act
        payload = {"name": "Japan", "code": "JP"}
        response = await client.put(f"/countries/{country.id}", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == country.id
        assert data["name"] == "Japan"
        assert data["code"] == "JP"

        # Verify database state
        await db_session.refresh(country)
        assert country.name == "Japan"

        # Verify event log
        event_result = await db_session.execute(select(EventLog))
        event_logs = event_result.scalars().all()
        assert len(event_logs) == 1
        assert event_logs[0].event_type == "UPDATE"
        assert event_logs[0].entity_type == "country"
        assert event_logs[0].entity_id == country.id
        assert event_logs[0].request_method == "PUT"
        assert event_logs[0].request_path == f"/countries/{country.id}"
        assert event_logs[0].ip_address is not None
        assert event_logs[0].processing_status == "completed"

    async def test_update_country_not_found(self, client: AsyncClient):
        """Test updating a non-existent country."""
        # Act
        payload = {"name": "Japan", "code": "JP"}
        response = await client.put("/countries/999", json=payload)

        # Assert
        assert response.status_code == 404

    async def test_delete_country(self, client: AsyncClient, db_session: AsyncSession):
        """Test deleting a country."""
        # Arrange
        country = await create_country_async(db_session, name="Japan", code="JP")

        # Act
        response = await client.delete(f"/countries/{country.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == country.id

        # Verify database state
        result = await db_session.execute(select(Country))
        countries = result.scalars().all()
        assert len(countries) == 0

        # Verify event log
        event_result = await db_session.execute(select(EventLog))
        event_logs = event_result.scalars().all()
        assert len(event_logs) == 1
        assert event_logs[0].event_type == "DELETE"
        assert event_logs[0].entity_type == "country"
        assert event_logs[0].entity_id == country.id
        assert event_logs[0].request_method == "DELETE"
        assert event_logs[0].request_path == f"/countries/{country.id}"
        assert event_logs[0].ip_address is not None
        assert event_logs[0].processing_status == "completed"

    async def test_delete_country_not_found(self, client: AsyncClient):
        """Test deleting a non-existent country."""
        # Act
        response = await client.delete("/countries/999")

        # Assert
        assert response.status_code == 404

    async def test_create_country_invalid_code(self, client: AsyncClient):
        """Test creating a country with invalid ISO code."""
        # Act
        payload = {"name": "Invalid Country", "code": "INVALID"}
        response = await client.post("/countries/", json=payload)

        # Assert
        assert response.status_code == 422  # Validation error

    async def test_create_country_duplicate_code(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test creating a country with duplicate code."""
        # Arrange
        await create_country_async(db_session, name="Japan", code="JP")

        # Act
        payload = {"name": "Another Japan", "code": "JP"}
        response = await client.post("/countries/", json=payload)

        # Assert
        assert response.status_code == 409  # Conflict - duplicate code
        assert "already exists" in response.json()["detail"].lower()
