from httpx import AsyncClient
from pymongo.database import Database
import pytest
from redis import Redis

from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestCreateSimulationAccountEndpoint(TestFixture):
    async def test_create_simulation_account_success(self, async_client: AsyncClient, test_db: Database, test_cache: Redis):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)
        user = await test_db.simulation_profiles.find_one({'simulation_id': simulation['_id']})
        bank_device = await test_db.simulation_bank_devices.find_one({'simulation_id': simulation['_id']})

        simulation_account_data = {
            'account_name': user['name'],
            'bank_name': bank_device['bank_name'],
            'balance': 100000,
            'kyc': 3,
            'bvn': user['user_id'],
            'merchant': False,
            'opening_device': user['devices'][0],
            'simulation_id': simulation['_id']
        }

        create_response = await async_client.post(
            '/simulation_accounts',
            json=simulation_account_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        assert create_response.status_code == 201
        response_data = create_response.json()
        
        assert 'data' in response_data
        assert 'message' in response_data
        assert 'account_no' in response_data['data']
        assert response_data['message'] == 'Simulation Account created successfully'

    
    async def test_create_simulation_account_invalid_bvn(self, async_client: AsyncClient, test_db: Database, test_cache: Redis):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)
        user = await test_db.simulation_profiles.find_one({'simulation_id': simulation['_id']})
        bank_device = await test_db.simulation_bank_devices.find_one({'simulation_id': simulation['_id']})

        simulation_account_data = {
            'account_name': user['name'],
            'bank_name': bank_device['bank_name'],
            'balance': 100000,
            'kyc': 3,
            'bvn': 'random_bvn',
            'merchant': False,
            'opening_device': user['devices'][0],
            'simulation_id': simulation['_id']
        }

        create_response = await async_client.post(
            '/simulation_accounts',
            json=simulation_account_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        assert create_response.status_code == 404
        response_data = create_response.json()
        assert response_data['message'] == f"Simulation Profile not found: random_bvn"


    async def test_create_simulation_account_invalid_bvn(self, async_client: AsyncClient, test_db: Database, test_cache: Redis):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)
        user = await test_db.simulation_profiles.find_one({'simulation_id': simulation['_id']})
        bank_device = await test_db.simulation_bank_devices.find_one({'simulation_id': simulation['_id']})

        simulation_account_data = {
            'account_name': 'Random Name',
            'bank_name': bank_device['bank_name'],
            'balance': 100000,
            'kyc': 3,
            'bvn': user['user_id'],
            'merchant': False,
            'opening_device': user['devices'][0],
            'simulation_id': simulation['_id']
        }

        create_response = await async_client.post(
            '/simulation_accounts',
            json=simulation_account_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        assert create_response.status_code == 409
        response_data = create_response.json()
        assert response_data['message'] == f"Account name does not match BVN name: {user['name']}"

    
    async def test_create_simulation_account_validation_errors(self, async_client: AsyncClient, test_db: Database, test_cache: Redis):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)
        user = await test_db.simulation_profiles.find_one({'simulation_id': simulation['_id']})
        bank_device = await test_db.simulation_bank_devices.find_one({'simulation_id': simulation['_id']})

        simulation_account_data = {
            'bank_name': bank_device['bank_name'],
            'balance': 100000,
            'kyc': 3,
            'bvn': user['user_id'],
            'merchant': False,
            'opening_device': user['devices'][0],
            'simulation_id': simulation['_id']
        }

        create_response = await async_client.post(
            '/simulation_accounts',
            json=simulation_account_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        assert create_response.status_code == 422
        assert create_response.json()['message'] == '\'account_name\': Field required'
