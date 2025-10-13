"""Integration tests for State API endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.event_log import EventLog
from models.state import State
from tests.factories.country import create_country_async
from tests.factories.state import create_state_async


@pytest.mark.asyncio
class TestStateAPI:
    """Test cases for State API endpoints."""

    async def test_create_state(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test creating a new state."""
        # Arrange
        country = await create_country_async(db_session, name="Japan", code="JP")
        payload = {"country_id": country.id, "name": "Tokyo", "code": "JP-13"}

        # Act
        response = await client.post("/states/", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Tokyo"
        assert data["code"] == "JP-13"
        assert data["country_id"] == country.id
        assert "id" in data

        # Verify database state
        result = await db_session.execute(select(State))
        states = result.scalars().all()
        assert len(states) == 1
        assert states[0].name == "Tokyo"
        assert states[0].code == "JP-13"

        # Verify event log
        event_result = await db_session.execute(select(EventLog))
        event_logs = event_result.scalars().all()
        assert len(event_logs) == 1
        assert event_logs[0].event_type == "CREATE"
        assert event_logs[0].entity_type == "state"
        assert event_logs[0].entity_id == data["id"]
        assert event_logs[0].request_method == "POST"
        assert event_logs[0].request_path == "/states/"
        assert event_logs[0].ip_address is not None
        assert event_logs[0].processing_status == "completed"

    async def test_create_state_country_not_found(self, client: AsyncClient):
        """Test creating a state with non-existent country."""
        # Arrange
        payload = {"country_id": 999, "name": "Tokyo", "code": "JP-13"}

        # Act
        response = await client.post("/states/", json=payload)

        # Assert
        assert response.status_code == 404  # Country not found

    async def test_get_state(self, client: AsyncClient, db_session: AsyncSession):
        """Test retrieving a state by ID."""
        # Arrange
        country = await create_country_async(db_session, name="Japan", code="JP")
        state = await create_state_async(
            db_session, country_id=country.id, name="Tokyo", code="JP-13"
        )

        # Act
        response = await client.get(f"/states/{state.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == state.id
        assert data["name"] == "Tokyo"
        assert data["code"] == "JP-13"
        assert data["country_id"] == country.id

    async def test_get_state_not_found(self, client: AsyncClient):
        """Test retrieving a non-existent state."""
        # Act
        response = await client.get("/states/999")

        # Assert
        assert response.status_code == 404

    async def test_list_states(self, client: AsyncClient, db_session: AsyncSession):
        """Test listing states."""
        # Arrange
        country = await create_country_async(db_session, name="Japan", code="JP")
        await create_state_async(
            db_session, country_id=country.id, name="Tokyo", code="JP-13"
        )
        await create_state_async(
            db_session, country_id=country.id, name="Osaka", code="JP-27"
        )
        await create_state_async(
            db_session, country_id=country.id, name="Kyoto", code="JP-26"
        )

        # Act
        response = await client.get("/states/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("id" in state for state in data)
        assert all("name" in state for state in data)
        assert all("code" in state for state in data)
        assert all("country_id" in state for state in data)

    async def test_list_states_filtered_by_country(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test listing states filtered by country."""
        # Arrange
        country_jp = await create_country_async(db_session, name="Japan", code="JP")
        country_us = await create_country_async(
            db_session, name="United States", code="US"
        )
        await create_state_async(
            db_session, country_id=country_jp.id, name="Tokyo", code="JP-13"
        )
        await create_state_async(
            db_session, country_id=country_jp.id, name="Osaka", code="JP-27"
        )
        await create_state_async(
            db_session, country_id=country_us.id, name="California", code="US-CA"
        )

        # Act
        response = await client.get(f"/states/?country_id={country_jp.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(s["country_id"] == country_jp.id for s in data)

    async def test_list_country_states_nested(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test listing states for a specific country (nested endpoint)."""
        # Arrange
        country_jp = await create_country_async(db_session, name="Japan", code="JP")
        country_us = await create_country_async(
            db_session, name="United States", code="US"
        )
        await create_state_async(
            db_session, country_id=country_jp.id, name="Tokyo", code="JP-13"
        )
        await create_state_async(
            db_session, country_id=country_jp.id, name="Osaka", code="JP-27"
        )
        await create_state_async(
            db_session, country_id=country_us.id, name="California", code="US-CA"
        )

        # Act
        response = await client.get(f"/countries/{country_jp.id}/states")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(s["country_id"] == country_jp.id for s in data)

    async def test_list_country_states_country_not_found(self, client: AsyncClient):
        """Test listing states for non-existent country."""
        # Act
        response = await client.get("/countries/999/states")

        # Assert
        assert response.status_code == 404

    async def test_list_states_pagination(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test listing states with pagination parameters."""
        # Arrange
        country = await create_country_async(db_session, name="Japan", code="JP")
        await create_state_async(
            db_session, country_id=country.id, name="Tokyo", code="JP-13"
        )
        await create_state_async(
            db_session, country_id=country.id, name="Osaka", code="JP-27"
        )
        await create_state_async(
            db_session, country_id=country.id, name="Kyoto", code="JP-26"
        )

        # Act
        response = await client.get("/states/?skip=1&limit=1")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    async def test_update_state(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating a state."""
        # Arrange
        country = await create_country_async(db_session, name="Japan", code="JP")
        state = await create_state_async(
            db_session, country_id=country.id, name="Toukyou", code="JP-13"
        )

        # Act
        payload = {"name": "Tokyo"}
        response = await client.put(f"/states/{state.id}", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == state.id
        assert data["name"] == "Tokyo"
        assert data["code"] == "JP-13"

        # Verify database state
        await db_session.refresh(state)
        assert state.name == "Tokyo"

        # Verify event log
        event_result = await db_session.execute(select(EventLog))
        event_logs = event_result.scalars().all()
        assert len(event_logs) == 1
        assert event_logs[0].event_type == "UPDATE"
        assert event_logs[0].entity_type == "state"
        assert event_logs[0].entity_id == state.id
        assert event_logs[0].request_method == "PUT"
        assert event_logs[0].request_path == f"/states/{state.id}"
        assert event_logs[0].ip_address is not None
        assert event_logs[0].processing_status == "completed"

    async def test_update_state_not_found(self, client: AsyncClient):
        """Test updating a non-existent state."""
        # Act
        payload = {"name": "Tokyo"}
        response = await client.put("/states/999", json=payload)

        # Assert
        assert response.status_code == 404

    async def test_delete_state(self, client: AsyncClient, db_session: AsyncSession):
        """Test deleting a state."""
        # Arrange
        country = await create_country_async(db_session, name="Japan", code="JP")
        state = await create_state_async(
            db_session, country_id=country.id, name="Tokyo", code="JP-13"
        )

        # Act
        response = await client.delete(f"/states/{state.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == state.id

        # Verify database state
        result = await db_session.execute(select(State))
        states = result.scalars().all()
        assert len(states) == 0

        # Verify event log
        event_result = await db_session.execute(select(EventLog))
        event_logs = event_result.scalars().all()
        assert len(event_logs) == 1
        assert event_logs[0].event_type == "DELETE"
        assert event_logs[0].entity_type == "state"
        assert event_logs[0].entity_id == state.id
        assert event_logs[0].request_method == "DELETE"
        assert event_logs[0].request_path == f"/states/{state.id}"
        assert event_logs[0].ip_address is not None
        assert event_logs[0].processing_status == "completed"

    async def test_delete_state_not_found(self, client: AsyncClient):
        """Test deleting a non-existent state."""
        # Act
        response = await client.delete("/states/999")

        # Assert
        assert response.status_code == 404

    async def test_create_state_invalid_code(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating a state with invalid ISO 3166-2 code."""
        # Arrange
        country = await create_country_async(db_session, name="Japan", code="JP")

        # Act
        payload = {"country_id": country.id, "name": "Tokyo", "code": "INVALID"}
        response = await client.post("/states/", json=payload)

        # Assert
        assert response.status_code == 422  # Validation error

    async def test_create_state_duplicate_code(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test creating a state with duplicate code."""
        # Arrange
        country = await create_country_async(db_session, name="Japan", code="JP")
        await create_state_async(
            db_session, country_id=country.id, name="Tokyo", code="JP-13"
        )

        # Act
        payload = {"country_id": country.id, "name": "Another Tokyo", "code": "JP-13"}
        response = await client.post("/states/", json=payload)

        # Assert
        assert response.status_code == 409  # Conflict - duplicate code
        assert "already exists" in response.json()["detail"].lower()

    async def test_delete_country_with_states_restricted(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test that deleting a country with states is restricted."""
        # Arrange
        country = await create_country_async(db_session, name="Japan", code="JP")
        await create_state_async(
            db_session, country_id=country.id, name="Tokyo", code="JP-13"
        )

        # Act
        response = await client.delete(f"/countries/{country.id}")

        # Assert
        assert response.status_code == 400  # Foreign key constraint violation
