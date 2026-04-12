from httpx import AsyncClient
from pymongo.database import Database
from bson import ObjectId
import pytest

from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestAnalyzeSimulationProfileEndpoint(TestFixture):
    async def test_analyze_simulation_profile_success(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)
        profile = await test_db.simulation_profiles.find_one({'simulation_id': str(simulation['_id'])})

        get_resp = await async_client.get(f"/simulation_profiles/{profile['_id']}/analyze", headers={'Authorization': f'Bearer {self.token}'})
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert 'numerical' in data['data'].keys()
        assert 'categorical' in data['data'].keys()


    async def test_analyze_simulation_profile_not_found(self, async_client: AsyncClient, test_db):
        await self._set_up(test_db)
        missing_id = str(ObjectId())
        get_resp = await async_client.get(f"/simulation_profiles/{missing_id}/analyze", headers={'Authorization': f'Bearer {self.token}'})
        assert get_resp.status_code == 404
        assert get_resp.json()['message'] == f'Simulation Profile not found: {missing_id}'
