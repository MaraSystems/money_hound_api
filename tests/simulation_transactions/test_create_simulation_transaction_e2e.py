from httpx import AsyncClient
from pymongo import DESCENDING
from pymongo.database import Database
import pytest
from redis import Redis

from src.config.config import ENV, ENVIRONMENTS
from src.domains.users.model import User
from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestCreateSimulationTransctionEndpoint(TestFixture):
    @pytest.mark.only
    async def test_create_simulation_transaction_success(self, async_client: AsyncClient, test_db: Database, test_cache: Redis):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)
        [last_simulation_transaction] = (await test_db.simulation_transactions.find({'simulation_id': simulation['_id']})
            .sort('time', DESCENDING)
            .limit(1).to_list()
        )

        simulation_transaction_data = {
            'amount': 100,
            'holder': last_simulation_transaction['holder'],
            'holder_bank': last_simulation_transaction['holder_bank'],
            'related': last_simulation_transaction['holder'],
            'related_bank': last_simulation_transaction['holder_bank'],
            'latitude': last_simulation_transaction['latitude'],
            'longitude': last_simulation_transaction['longitude'],
            'type': 'DEBIT',
            'category': 'WITHDRAWAL',
            'channel': 'APP',
            'device': last_simulation_transaction['holder'],
            'simulation_id': simulation['_id']
        }

        create_response = await async_client.post(
            '/simulation_transactions',
            json=simulation_transaction_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        assert create_response.status_code == 201
        # response_data = create_response.json()
        
        # assert 'data' in response_data
        # assert 'message' in response_data
        # assert response_data['data']['title'] == 'Random'
        # assert response_data['data']['description'] == 'Administrator role'
        # assert response_data['data']['permissions'] == ['*:*:*']
        # assert response_data['data']['author_id'] is not None
        # assert response_data['message'] == 'Role created successfully: Random'


    async def test_create_simulation_transaction_unauthorized(self, async_client: AsyncClient):
        role_data = {
            'title': 'Admin',
            'description': 'Administrator role',
            'permissions': ['*:*:*']
        }
        
        create_response = await async_client.post('/simulation_transactions', json=role_data)
        
        assert create_response.status_code == 401
        response_data = create_response.json()
        assert 'message' in response_data


    async def test_create_simulation_transaction_invalid_token(self, async_client: AsyncClient):
        role_data = {
            'title': 'Admin',
            'description': 'Administrator role',
            'permissions': ['*:*:*']
        }
        
        create_response = await async_client.post(
            '/simulation_transactions',
            json=role_data,
            headers={'Authorization': 'Bearer invalid_token'}
        )
        
        assert create_response.status_code == 401
        response_data = create_response.json()
        assert response_data['message'] == 'Token is invalid'


    async def test_create_simulation_transaction_validation_errors(self, async_client: AsyncClient, test_db: Database):
        await self._set_up(test_db)

        # Test: Create role with missing required fields
        invalid_role_data = {
            'description': 'Role without title'
        }
        
        create_response = await async_client.post(
            '/simulation_transactions',
            json=invalid_role_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        assert create_response.status_code == 422
        assert create_response.json()['message'] == '\'title\': Field required'
