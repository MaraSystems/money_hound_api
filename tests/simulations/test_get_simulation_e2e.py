from httpx import AsyncClient
from pymongo.database import Database
from bson import ObjectId
import pytest

from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestGetSimulationEndpoint(TestFixture):
    async def test_get_simulation_success(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)

        get_resp = await async_client.get(f"/simulations/{simulation['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert data['data']['_id'] == str(simulation['_id'])
        assert data['data']['author_id'] == str(self.user['_id'])


    async def test_get_simulation_not_found(self, async_client: AsyncClient, test_db):
        await self._set_up(test_db)
        missing_id = str(ObjectId())
        get_resp = await async_client.get(f'/simulations/{missing_id}', headers={'Authorization': f'Bearer {self.token}'})
        assert get_resp.status_code == 404
        assert get_resp.json()['message'] == f'Simulation not found: {missing_id}'


    async def test_get_simulation_hidden_returns_404(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)

        # Soft-delete (hide) the role
        del_resp = await async_client.delete(f"/simulations/{simulation['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert del_resp.status_code == 200

        # Now fetching should return 404 because hidden roles are excluded
        get_resp = await async_client.get(f"/simulations/{simulation['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert get_resp.status_code == 404
        assert get_resp.json()['message'] == f"Simulation not found: {simulation['_id']}"
