from bson import ObjectId
from httpx import AsyncClient
from pymongo.database import Database
import pytest
from redis import Redis

from src.domains.roles.model import CreateRole
from src.domains.users.model import User
from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestDeleteSimulationEndpoint(TestFixture):
    async def test_delete_simulation_success(self, async_client: AsyncClient, test_db: Database, test_cache: Redis):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)

        del_resp = await async_client.delete(f"/simulations/{simulation['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert del_resp.status_code == 200
        assert del_resp.json()['message'] == 'Simulation deleted successfully'

        get_resp2 = await async_client.get(f"/simulations/{simulation['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert get_resp2.status_code == 404


    async def test_delete_simulation_not_found(self, async_client: AsyncClient, test_db):
        await self._set_up(test_db)        
        missing_id = '66f2f2f2f2f2f2f2f2f2f2f2'  # any ObjectId-like string
        del_resp = await async_client.delete(f"/simulations/{missing_id}", headers={'Authorization': f'Bearer {self.token}'})
        assert del_resp.status_code == 404
        assert del_resp.json()['message'].startswith('Simulation not found:')


    async def test_delete_simulation_preserves_other_fields(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)

        del_resp = await async_client.delete(f"/simulations/{simulation['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert del_resp.status_code == 200

        stored = await test_db.simulations.find_one({'_id': ObjectId(simulation['_id'])})
        assert stored['days'] == simulation['days']
        assert stored['hidden'] is True
