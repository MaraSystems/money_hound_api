from httpx import AsyncClient
from pymongo.database import Database
from bson import ObjectId
import pytest

from tests.fixture_spec import TestFixture

@pytest.mark.asyncio
class TestGetSimulationBankDeviceEndpoint(TestFixture):
    async def test_get_simulation_bank_device_success(self, async_client: AsyncClient, test_db: Database, test_cache):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)

        bank_device = await test_db.simulation_bank_devices.find_one({'simulation_id': str(simulation['_id'])})
        get_resp = await async_client.get(f"/simulation_bank_devices/{bank_device['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert get_resp.status_code == 200
        data = get_resp.json()

        assert data['data']['_id'] == str(bank_device['_id'])


    async def test_get_simulation_bank_device_not_found(self, async_client: AsyncClient, test_db):
        await self._set_up(test_db)
        missing_id = str(ObjectId())
        get_resp = await async_client.get(f"/simulation_bank_devices/{missing_id}", headers={'Authorization': f'Bearer {self.token}'})
        assert get_resp.status_code == 404
        assert get_resp.json()['message'] == f'Simulation Bank Device not found: {missing_id}'
