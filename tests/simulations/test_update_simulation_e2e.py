import email
from fastapi import status
from httpx import AsyncClient
from pymongo.database import Database
import pytest

from src.domains.auth.model import CreateUser
from src.domains.roles.model import CreateRole
from src.domains.users.model import User
from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestUpdateSimulationEndpoint(TestFixture):
    
    async def test_update_simulation_success(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)
        update_payload = {'days': 3}
        resp = await async_client.patch(f"/simulations/{simulation['_id']}", json=update_payload, headers={'Authorization': f'Bearer {self.token}'})

        assert resp.status_code == 200
        data = resp.json()
        assert data['data']['days'] == 3
        assert data['message'] == 'Simulation re-initiated successfully'

    
    async def test_update_simulation_not_authorized(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)

        user = CreateUser(**{**self.user_data.model_dump(), 'email':'r@r.r'})
        await self._create_user(test_db, user)
        token = self._assign_token(user)

        resp = await async_client.patch(f"/simulations/{simulation['_id']}", json={}, headers={'Authorization': f'Bearer {token}'})
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
        assert resp.json()['message'] == 'You are not authorized'
