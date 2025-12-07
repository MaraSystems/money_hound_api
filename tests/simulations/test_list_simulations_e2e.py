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
class TestListSimulationsEndpoint(TestFixture):
    
    async def test_list_simulations_success(self, async_client: AsyncClient, test_db: Database, test_cache: Redis):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)

        resp = await async_client.get('/simulations', headers={'Authorization': f'Bearer {self.token}'})
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data['data'], list)
        statuses = [item['status'] for item in data['data']]
        assert 'COMPLETE' in statuses

    
    async def test_list_simulations_query_filter(self, async_client: AsyncClient, test_db: Database, test_cache: Redis):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)

        resp = await async_client.get(f"/simulations?author_id={self.user['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data['data']) >= 1
        assert data['data'][0]['author_id'] == str(self.user['_id'])

    
    async def test_list_simulations_excludes_hidden(self, async_client: AsyncClient, test_db: Database, test_cache: Redis):
        await self._set_up(test_db)
        hidden = await self._create_simulation(test_db, test_cache)
        
        # Soft delete the hidden one
        del_resp = await async_client.delete(f"/simulations/{hidden['_id']}", headers={'Authorization': f'Bearer {self.token}'})
        assert del_resp.status_code == 200

        resp = await async_client.get('/simulations', headers={'Authorization': f'Bearer {self.token}'})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data['data']) == 0


    async def test_list_simulations_pagination(self, async_client: AsyncClient, test_db: Database, test_cache: Redis):
        await self._set_up(test_db)

        # Create 5 roles
        for i in range(5):
            await self._create_simulation(test_db, test_cache)


        # Limit
        resp = await async_client.get('/simulations?limit=2', headers={'Authorization': f'Bearer {self.token}'})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data['data']) == 2

        # Skip + limit
        resp2 = await async_client.get('/simulations?skip=2&limit=2', headers={'Authorization': f'Bearer {self.token}'})
        assert resp2.status_code == 200
        data2 = resp2.json()
        assert len(data2['data']) == 2
