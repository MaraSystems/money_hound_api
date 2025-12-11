from httpx import AsyncClient
from pymongo import DESCENDING
from pymongo.database import Database
import pytest
from redis import Redis

from tests.fixture_spec import TestFixture


@pytest.mark.asyncio
class TestCreateSimulationTransctionEndpoint(TestFixture):
    async def test_create_simulation_transaction_success(self, async_client: AsyncClient, test_db: Database, test_cache: Redis):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)
        [holder_account, related_account] = (await test_db.simulation_accounts.find({'simulation_id': simulation['_id'], 'balance': {'$gt': 100}})
            .limit(2).to_list()
        )

        user = await test_db.simulation_profiles.find_one({'simulation_id': simulation['_id'], 'user_id': holder_account['bvn']})
        amount = holder_account['balance']/2
        amount = 1000 if amount < 1000 else amount
        simulation_transaction_data = {
            'amount': amount,
            'holder': holder_account['account_no'],
            'holder_bank': holder_account['bank_name'],
            'related': related_account['account_no'],
            'related_bank': related_account['bank_name'],
            'latitude': user['latitude'],
            'longitude': user['longitude'],
            'type': 'DEBIT',
            'category': 'WITHDRAWAL',
            'channel': 'APP',
            'device': holder_account['opening_device'],
            'simulation_id': simulation['_id']
        }

        create_response = await async_client.post(
            '/simulation_transactions',
            json=simulation_transaction_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        assert create_response.status_code == 201
        response_data = create_response.json()
        
        assert 'data' in response_data
        assert 'message' in response_data
        assert response_data['message'] == 'Transaction created successfully'

    
    async def test_create_simulation_transaction_insufficient(self, async_client: AsyncClient, test_db: Database, test_cache: Redis):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)
        [holder_account, related_account] = (await test_db.simulation_accounts.find({'simulation_id': simulation['_id']})
            .limit(2).to_list()
        )

        user = await test_db.simulation_profiles.find_one({'simulation_id': simulation['_id'], 'user_id': holder_account['bvn']})

        simulation_transaction_data = {
            'amount': holder_account['balance'] + 1000,
            'holder': holder_account['account_no'],
            'holder_bank': holder_account['bank_name'],
            'related': related_account['account_no'],
            'related_bank': related_account['bank_name'],
            'latitude': user['latitude'],
            'longitude': user['longitude'],
            'type': 'DEBIT',
            'category': 'WITHDRAWAL',
            'channel': 'APP',
            'device': holder_account['opening_device'],
            'simulation_id': simulation['_id']
        }

        create_response = await async_client.post(
            '/simulation_transactions',
            json=simulation_transaction_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        assert create_response.status_code == 409
        response_data = create_response.json()
        assert response_data['message'] == f"Insufficient Fund: {holder_account['balance']}"


    async def test_create_simulation_transaction_validation_errors(self, async_client: AsyncClient, test_db: Database, test_cache: Redis):
        await self._set_up(test_db)
        simulation = await self._create_simulation(test_db, test_cache)
        [holder_account, related_account] = (await test_db.simulation_accounts.find({'simulation_id': simulation['_id'], 'balance': {'$gt': 100}})
            .limit(2).to_list()
        )

        user = await test_db.simulation_profiles.find_one({'simulation_id': simulation['_id'], 'user_id': holder_account['bvn']})

        simulation_transaction_data = {
            'holder': holder_account['account_no'],
            'holder_bank': holder_account['bank_name'],
            'related': related_account['account_no'],
            'related_bank': related_account['bank_name'],
            'latitude': user['latitude'],
            'longitude': user['longitude'],
            'type': 'DEBIT',
            'category': 'WITHDRAWAL',
            'channel': 'APP',
            'device': holder_account['opening_device'],
            'simulation_id': simulation['_id']
        }

        create_response = await async_client.post(
            '/simulation_transactions',
            json=simulation_transaction_data,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        
        assert create_response.status_code == 422
        assert create_response.json()['message'] == '\'amount\': Field required'
