from httpx import AsyncClient
from pymongo.database import Database
from bson import ObjectId
from pytest import mark
import pytest
from redis import Redis

from src.domains.simulations.model import CreateSimulation
from src.domains.users.model import User
from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestListSimulationTransactionsEndpoint(TestFixture):
    async def test_list_simulation_transactions_success(self, async_client: AsyncClient, test_db: Database, test_cache: Redis):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)

        resp = await async_client.get(f"/simulation_transactions?simulation_id={simulation['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data['data'], list)
        assert data['data'][0]['simulation_id'] == str(simulation['_id'])


    async def test_list_simulation_transactions_query_filter(self, async_client: AsyncClient, test_db: Database, test_cache: Redis):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)

        resp = await async_client.get(f"/simulation_transactions?simulation_id={simulation['_id']}&type=DEBIT", headers={'Authorization': f'Bearer {self.token}'})
        assert resp.status_code == 200
        data = resp.json()
        
        debits = [t for t in data['data'] if t['type'] == 'DEBIT']
        assert len(data['data']) == len(debits)


    async def test_list_simulation_transactions_pagination(self, async_client: AsyncClient, test_db: Database, test_cache: Redis):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)

        # Limit
        resp = await async_client.get(f"/simulation_transactions?simulation_id={simulation['_id']}&limit=2", headers={'Authorization': f'Bearer {self.token}'})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data['data']) == 2
