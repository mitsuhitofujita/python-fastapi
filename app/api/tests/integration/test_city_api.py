"""Integration tests for City API endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.city import City
from models.event_log import EventLog
from tests.factories.city import create_city_async
from tests.factories.state import create_state_async


@pytest.mark.asyncio
class TestCityAPI:
    """Test cases for City API endpoints."""

    async def test_create_city(self, client: AsyncClient, db_session: AsyncSession):
        """Test creating a new city."""
        # Arrange
        state = await create_state_async(db_session)
        payload = {
            "state_id": state.id,
            "name": "港区",
            "code": "131016",
            "is_active": True,
        }

        # Act
        response = await client.post("/cities/", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "港区"
        assert data["code"] == "131016"
        assert data["state_id"] == state.id
        assert data["is_active"] is True
        assert "id" in data

        # Verify database record
        result = await db_session.execute(select(City).where(City.id == data["id"]))
        city_in_db = result.scalar_one_or_none()
        assert city_in_db is not None
        assert city_in_db.name == "港区"
        assert city_in_db.code == "131016"
        assert city_in_db.state_id == state.id
        assert city_in_db.is_active is True

        # Verify event log
        result = await db_session.execute(
            select(EventLog)
            .where(EventLog.entity_type == "city")
            .where(EventLog.event_type == "CREATE")
            .where(EventLog.entity_id == data["id"])
        )
        event = result.scalar_one_or_none()
        assert event is not None
        assert event.request_method == "POST"
        assert event.request_path == "/cities/"
        assert event.processing_status == "completed"

    async def test_get_city(self, client: AsyncClient, db_session: AsyncSession):
        """Test getting a city by ID."""
        # Arrange
        city = await create_city_async(db_session)

        # Act
        response = await client.get(f"/cities/{city.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == city.id
        assert data["name"] == city.name
        assert data["code"] == city.code
        assert data["state_id"] == city.state_id
        assert data["is_active"] == city.is_active

    async def test_list_cities(self, client: AsyncClient, db_session: AsyncSession):
        """Test listing cities."""
        # Arrange - create 3 cities
        await create_city_async(db_session, name="港区", code="131016")
        await create_city_async(db_session, name="渋谷区", code="131130")
        await create_city_async(db_session, name="新宿区", code="131041")

        # Act
        response = await client.get("/cities/")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        # Verify all cities are active by default
        assert all(city["is_active"] is True for city in data)

    async def test_list_cities_pagination(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test listing cities with pagination."""
        # Arrange - create 3 cities
        await create_city_async(db_session, name="City 1", code="111111")
        city2 = await create_city_async(db_session, name="City 2", code="222222")
        await create_city_async(db_session, name="City 3", code="333333")

        # Act - get the second city only (skip=1, limit=1)
        response = await client.get("/cities/?skip=1&limit=1")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        # Should return the second city
        assert data[0]["id"] == city2.id

    async def test_list_cities_by_state(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test listing cities filtered by state."""
        # Arrange - create 2 states with 2 cities each
        state1 = await create_state_async(db_session)
        state2 = await create_state_async(db_session)

        city1_state1 = await create_city_async(
            db_session, state_id=state1.id, name="City 1-1", code="111111"
        )
        city2_state1 = await create_city_async(
            db_session, state_id=state1.id, name="City 1-2", code="111112"
        )

        city1_state2 = await create_city_async(
            db_session, state_id=state2.id, name="City 2-1", code="222221"
        )
        city2_state2 = await create_city_async(
            db_session, state_id=state2.id, name="City 2-2", code="222222"
        )

        # Act - get cities for state1
        response = await client.get(f"/states/{state1.id}/cities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Verify only cities from state1 are returned
        city_ids = [city["id"] for city in data]
        assert city1_state1.id in city_ids
        assert city2_state1.id in city_ids
        assert city1_state2.id not in city_ids
        assert city2_state2.id not in city_ids

    async def test_update_city(self, client: AsyncClient, db_session: AsyncSession):
        """Test updating a city."""
        # Arrange
        city = await create_city_async(db_session, name="港区", code="131016")
        payload = {"name": "横浜市鶴見区", "code": "141003"}

        # Act
        response = await client.put(f"/cities/{city.id}", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == city.id
        assert data["name"] == "横浜市鶴見区"
        assert data["code"] == "141003"
        assert data["state_id"] == city.state_id  # state_id should not change

        # Verify database record
        result = await db_session.execute(select(City).where(City.id == city.id))
        city_in_db = result.scalar_one_or_none()
        assert city_in_db is not None
        assert city_in_db.name == "横浜市鶴見区"
        assert city_in_db.code == "141003"
        assert city_in_db.state_id == city.state_id
        assert city_in_db.is_active is True

        # Verify event log
        result = await db_session.execute(
            select(EventLog)
            .where(EventLog.entity_type == "city")
            .where(EventLog.event_type == "UPDATE")
            .where(EventLog.entity_id == city.id)
        )
        event = result.scalar_one_or_none()
        assert event is not None
        assert event.request_method == "PUT"
        assert event.request_path == f"/cities/{city.id}"
        assert event.processing_status == "completed"

    async def test_delete_city(self, client: AsyncClient, db_session: AsyncSession):
        """Test deleting a city."""
        # Arrange
        city = await create_city_async(db_session)

        # Act
        response = await client.delete(f"/cities/{city.id}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == city.id

        # Verify city is deleted
        result = await db_session.execute(select(City).where(City.id == city.id))
        deleted_city = result.scalar_one_or_none()
        assert deleted_city is None

        # Verify event log
        result = await db_session.execute(
            select(EventLog)
            .where(EventLog.entity_type == "city")
            .where(EventLog.event_type == "DELETE")
            .where(EventLog.entity_id == city.id)
        )
        event = result.scalar_one_or_none()
        assert event is not None
        assert event.request_method == "DELETE"
        assert event.request_path == f"/cities/{city.id}"
        assert event.processing_status == "completed"

    async def test_create_city_inactive(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test creating a city with is_active=False."""
        # Arrange
        state = await create_state_async(db_session)
        payload = {
            "state_id": state.id,
            "name": "津久井町",
            "code": "143626",
            "is_active": False,
        }

        # Act
        response = await client.post("/cities/", json=payload)

        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "津久井町"
        assert data["code"] == "143626"
        assert data["is_active"] is False
        assert "id" in data

        # Verify event log
        result = await db_session.execute(
            select(EventLog)
            .where(EventLog.entity_type == "city")
            .where(EventLog.event_type == "CREATE")
            .where(EventLog.entity_id == data["id"])
        )
        event = result.scalar_one_or_none()
        assert event is not None

    async def test_update_city_deactivate(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test deactivating a city by setting is_active to False."""
        # Arrange - create active city
        city = await create_city_async(db_session, name="港区", code="131016")
        payload = {"is_active": False}

        # Act - deactivate the city
        response = await client.put(f"/cities/{city.id}", json=payload)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["is_active"] is False

        # Verify default GET returns 404 for inactive city
        response_get = await client.get(f"/cities/{city.id}")
        assert response_get.status_code == 404

        # Verify GET with include_inactive=true returns the city
        response_get_inactive = await client.get(
            f"/cities/{city.id}?include_inactive=true"
        )
        assert response_get_inactive.status_code == 200
        data_inactive = response_get_inactive.json()
        assert data_inactive["id"] == city.id
        assert data_inactive["is_active"] is False

    async def test_list_cities_include_inactive(
        self, client: AsyncClient, db_session: AsyncSession
    ):
        """Test listing cities with include_inactive parameter."""
        # Arrange - create 2 active cities and 1 inactive city
        await create_city_async(db_session, name="港区", code="131016", is_active=True)
        await create_city_async(
            db_session, name="渋谷区", code="131130", is_active=True
        )
        await create_city_async(
            db_session, name="津久井町", code="143626", is_active=False
        )

        # Act - list without include_inactive (should return 2)
        response_active_only = await client.get("/cities/")
        assert response_active_only.status_code == 200
        data_active_only = response_active_only.json()
        assert len(data_active_only) == 2

        # Act - list with include_inactive=true (should return 3)
        response_all = await client.get("/cities/?include_inactive=true")
        assert response_all.status_code == 200
        data_all = response_all.json()
        assert len(data_all) == 3
        # Verify we have both active and inactive cities
        active_count = sum(1 for city in data_all if city["is_active"])
        inactive_count = sum(1 for city in data_all if not city["is_active"])
        assert active_count == 2
        assert inactive_count == 1
