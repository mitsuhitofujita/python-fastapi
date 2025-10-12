"""Unit tests for State CRUD operations."""

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from crud.country import RequestInfo
from crud.state import (
    create_state,
    delete_state,
    get_state,
    get_states,
    update_state,
)
from models.country import Country
from models.event_log import EventLog
from models.state import State
from schemas.state import StateCreate, StateUpdate


@pytest.mark.asyncio
class TestStateCRUD:
    """Test cases for State CRUD operations."""

    async def test_create_state(self, db_session: AsyncSession):
        """Test creating a state records event log."""
        # Arrange - Create country first
        country = Country(name="Japan", code="JP")
        db_session.add(country)
        await db_session.commit()
        await db_session.refresh(country)

        state_data = StateCreate(country_id=country.id, name="Tokyo", code="JP-13")
        request_info = RequestInfo(
            method="POST",
            path=f"/countries/{country.id}/states",
            body='{"name": "Tokyo", "code": "JP-13"}',
            ip_address="127.0.0.1",
            status_code=201,
        )

        # Act
        state = await create_state(db_session, state_data, request_info)

        # Assert - State created
        assert state.id is not None
        assert state.country_id == country.id
        assert state.name == "Tokyo"
        assert state.code == "JP-13"

        # Assert - Event log created
        result = await db_session.execute(select(EventLog))
        event_logs = result.scalars().all()
        assert len(event_logs) == 1
        assert event_logs[0].event_type == "CREATE"
        assert event_logs[0].entity_type == "state"
        assert event_logs[0].entity_id == state.id
        assert event_logs[0].request_method == "POST"
        assert event_logs[0].processing_status == "completed"

    async def test_create_state_invalid_country(self, db_session: AsyncSession):
        """Test creating a state with non-existent country fails."""
        # Arrange
        state_data = StateCreate(country_id=999, name="Tokyo", code="JP-13")
        request_info = RequestInfo(
            method="POST",
            path="/countries/999/states",
            body='{"name": "Tokyo", "code": "JP-13"}',
            ip_address="127.0.0.1",
            status_code=400,
        )

        # Act & Assert
        with pytest.raises(IntegrityError):
            await create_state(db_session, state_data, request_info)

    async def test_get_state(self, db_session: AsyncSession):
        """Test retrieving a state by ID."""
        # Arrange
        country = Country(name="Japan", code="JP")
        db_session.add(country)
        await db_session.commit()
        await db_session.refresh(country)

        state = State(country_id=country.id, name="Tokyo", code="JP-13")
        db_session.add(state)
        await db_session.commit()
        await db_session.refresh(state)

        # Act
        result = await get_state(db_session, state.id)

        # Assert
        assert result is not None
        assert result.id == state.id
        assert result.name == "Tokyo"
        assert result.code == "JP-13"
        assert result.country_id == country.id

    async def test_get_state_not_found(self, db_session: AsyncSession):
        """Test retrieving a non-existent state."""
        # Act
        result = await get_state(db_session, 999)

        # Assert
        assert result is None

    async def test_get_states(self, db_session: AsyncSession):
        """Test retrieving all states."""
        # Arrange
        country = Country(name="Japan", code="JP")
        db_session.add(country)
        await db_session.commit()
        await db_session.refresh(country)

        states_data = [
            State(country_id=country.id, name="Tokyo", code="JP-13"),
            State(country_id=country.id, name="Osaka", code="JP-27"),
            State(country_id=country.id, name="Kyoto", code="JP-26"),
        ]
        for state in states_data:
            db_session.add(state)
        await db_session.commit()

        # Act
        result = await get_states(db_session)

        # Assert
        assert len(result) == 3
        assert all(isinstance(s, State) for s in result)

    async def test_get_states_filtered_by_country(self, db_session: AsyncSession):
        """Test retrieving states filtered by country."""
        # Arrange
        country_jp = Country(name="Japan", code="JP")
        country_us = Country(name="United States", code="US")
        db_session.add(country_jp)
        db_session.add(country_us)
        await db_session.commit()
        await db_session.refresh(country_jp)
        await db_session.refresh(country_us)

        states_data = [
            State(country_id=country_jp.id, name="Tokyo", code="JP-13"),
            State(country_id=country_jp.id, name="Osaka", code="JP-27"),
            State(country_id=country_us.id, name="California", code="US-CA"),
        ]
        for state in states_data:
            db_session.add(state)
        await db_session.commit()

        # Act
        result = await get_states(db_session, country_id=country_jp.id)

        # Assert
        assert len(result) == 2
        assert all(s.country_id == country_jp.id for s in result)

    async def test_get_states_pagination(self, db_session: AsyncSession):
        """Test retrieving states with pagination."""
        # Arrange
        country = Country(name="Japan", code="JP")
        db_session.add(country)
        await db_session.commit()
        await db_session.refresh(country)

        states_data = [
            State(country_id=country.id, name="Tokyo", code="JP-13"),
            State(country_id=country.id, name="Osaka", code="JP-27"),
            State(country_id=country.id, name="Kyoto", code="JP-26"),
        ]
        for state in states_data:
            db_session.add(state)
        await db_session.commit()

        # Act
        result = await get_states(db_session, skip=1, limit=1)

        # Assert
        assert len(result) == 1

    async def test_update_state(self, db_session: AsyncSession):
        """Test updating a state records event log."""
        # Arrange
        country = Country(name="Japan", code="JP")
        db_session.add(country)
        await db_session.commit()
        await db_session.refresh(country)

        state = State(country_id=country.id, name="Toukyou", code="JP-13")
        db_session.add(state)
        await db_session.commit()
        await db_session.refresh(state)

        state_data = StateUpdate(name="Tokyo")
        request_info = RequestInfo(
            method="PUT",
            path=f"/states/{state.id}",
            body='{"name": "Tokyo"}',
            ip_address="127.0.0.1",
            status_code=200,
        )

        # Act
        result = await update_state(db_session, state.id, state_data, request_info)

        # Assert - State updated
        assert result is not None
        assert result.id == state.id
        assert result.name == "Tokyo"
        assert result.code == "JP-13"

        # Assert - Event log created
        event_result = await db_session.execute(select(EventLog))
        event_logs = event_result.scalars().all()
        assert len(event_logs) == 1
        assert event_logs[0].event_type == "UPDATE"
        assert event_logs[0].entity_id == state.id

    async def test_update_state_not_found(self, db_session: AsyncSession):
        """Test updating a non-existent state."""
        # Arrange
        state_data = StateUpdate(name="Tokyo")
        request_info = RequestInfo(
            method="PUT",
            path="/states/999",
            ip_address="127.0.0.1",
            status_code=404,
        )

        # Act
        result = await update_state(db_session, 999, state_data, request_info)

        # Assert
        assert result is None

    async def test_delete_state(self, db_session: AsyncSession):
        """Test deleting a state records event log."""
        # Arrange
        country = Country(name="Japan", code="JP")
        db_session.add(country)
        await db_session.commit()
        await db_session.refresh(country)

        state = State(country_id=country.id, name="Tokyo", code="JP-13")
        db_session.add(state)
        await db_session.commit()
        await db_session.refresh(state)
        state_id = state.id

        request_info = RequestInfo(
            method="DELETE",
            path=f"/states/{state_id}",
            ip_address="127.0.0.1",
            status_code=200,
        )

        # Act
        result = await delete_state(db_session, state_id, request_info)

        # Assert - State deleted
        assert result is not None
        assert result.id == state_id

        # Verify state no longer exists
        state_result = await db_session.execute(select(State))
        states = state_result.scalars().all()
        assert len(states) == 0

        # Assert - Event log created
        event_result = await db_session.execute(select(EventLog))
        event_logs = event_result.scalars().all()
        assert len(event_logs) == 1
        assert event_logs[0].event_type == "DELETE"
        assert event_logs[0].entity_id == state_id

    async def test_delete_state_not_found(self, db_session: AsyncSession):
        """Test deleting a non-existent state."""
        # Arrange
        request_info = RequestInfo(
            method="DELETE",
            path="/states/999",
            ip_address="127.0.0.1",
            status_code=404,
        )

        # Act
        result = await delete_state(db_session, 999, request_info)

        # Assert
        assert result is None

    async def test_foreign_key_restrict_on_delete(self, db_session: AsyncSession):
        """Test that deleting a country with states is restricted."""
        # Arrange
        country = Country(name="Japan", code="JP")
        db_session.add(country)
        await db_session.commit()
        await db_session.refresh(country)

        state = State(country_id=country.id, name="Tokyo", code="JP-13")
        db_session.add(state)
        await db_session.commit()

        # Act & Assert
        with pytest.raises(IntegrityError):
            await db_session.delete(country)
            await db_session.commit()
